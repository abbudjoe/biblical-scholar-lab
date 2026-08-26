from __future__ import annotations

import hashlib
import json
import os
import re
import stat
from dataclasses import dataclass
from pathlib import Path
from typing import Any, cast

import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import Response

from bsl.application.vs01_study_workspace import canonical_workspace_projection_bytes, compile_vs01_study_workspace
from bsl.infrastructure.study_workspace_authority import read_t06_page_asset

ROOT = Path(__file__).parents[3]
ARCHIVE_ROOT = Path("/Volumes/BSL-Archive/BiblicalScholarLab")
WEB_ROOT = ROOT / "web/dist"
MANIFEST_NAME = "asset-manifest.json"
SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "Referrer-Policy": "no-referrer",
    "Cross-Origin-Resource-Policy": "same-origin",
    "X-Frame-Options": "DENY",
    "Content-Security-Policy": (
        "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self'; connect-src 'self'; "
        "font-src 'self'; object-src 'none'; base-uri 'none'; form-action 'none'; frame-ancestors 'none'; "
        "worker-src 'none'; manifest-src 'none'"
    ),
}
MEDIA_TYPES = {
    ".html": "text/html; charset=utf-8",
    ".js": "text/javascript; charset=utf-8",
    ".css": "text/css; charset=utf-8",
}
SAFE_ASSET_PART = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]*")


@dataclass(frozen=True)
class ClientAsset:
    path: str
    media_type: str
    data: bytes
    etag: str


def _safe_parts(relative: str) -> tuple[str, ...]:
    parts = tuple(relative.split("/"))
    if (
        not parts
        or relative.startswith("/")
        or "\\" in relative
        or any(part in ("", ".", "..") or SAFE_ASSET_PART.fullmatch(part) is None for part in parts)
    ):
        raise ValueError("client asset path is unsafe")
    return parts


def _read_regular(root: Path, relative: str) -> bytes:
    parts = _safe_parts(relative)
    flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0)
    directory = os.open(root, flags)
    try:
        for part in parts[:-1]:
            child = os.open(part, flags, dir_fd=directory)
            os.close(directory)
            directory = child
        descriptor = os.open(parts[-1], os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0), dir_fd=directory)
        metadata = os.fstat(descriptor)
        with os.fdopen(descriptor, "rb") as stream:
            data = stream.read()
    except OSError:
        raise ValueError(f"client asset is unreadable: {Path(relative).name}") from None
    finally:
        os.close(directory)
    if not stat.S_ISREG(metadata.st_mode):
        raise ValueError("client asset is not a regular file")
    return data


def _client_assets(web_root: Path) -> dict[str, ClientAsset]:
    manifest_bytes = _read_regular(web_root, MANIFEST_NAME)
    try:
        parsed: object = json.loads(manifest_bytes)
    except (json.JSONDecodeError, KeyError, TypeError):
        raise ValueError("client asset manifest is invalid") from None
    if not isinstance(parsed, dict):
        raise ValueError("client asset manifest is invalid")
    manifest = cast(dict[str, Any], parsed)
    records_value = manifest.get("assets")
    if (
        set(manifest) != {"schema_version", "assets"}
        or manifest.get("schema_version") != "1.0"
        or not isinstance(records_value, list)
    ):
        raise ValueError("client asset manifest contract differs")
    records = cast(list[object], records_value)
    assets: dict[str, ClientAsset] = {}
    for value in records:
        if not isinstance(value, dict):
            raise ValueError("client asset manifest entry differs")
        record = cast(dict[str, Any], value)
        if set(record) != {"path", "media_type", "byte_count", "sha256"}:
            raise ValueError("client asset manifest entry differs")
        relative_value = record["path"]
        if not isinstance(relative_value, str) or relative_value == MANIFEST_NAME or relative_value in assets:
            raise ValueError("client asset manifest path differs")
        relative = relative_value
        data = _read_regular(web_root, relative)
        media_type = MEDIA_TYPES.get(Path(relative).suffix)
        digest = hashlib.sha256(data).hexdigest()
        if media_type is None or record != {
            "path": relative,
            "media_type": media_type,
            "byte_count": len(data),
            "sha256": digest,
        }:
            raise ValueError("client asset manifest authority differs")
        assets[relative] = ClientAsset(relative, media_type, data, f'"{digest}"')
    inventory = tuple(web_root.rglob("*"))
    if any(path.is_symlink() or not (path.is_file() or path.is_dir()) for path in inventory):
        raise ValueError("client asset manifest closure differs")
    actual_files = {path.relative_to(web_root).as_posix() for path in inventory if path.is_file() or path.is_symlink()}
    actual_directories = {
        path.relative_to(web_root).as_posix() for path in inventory if path.is_dir() and not path.is_symlink()
    }
    declared_directories = {
        parent.as_posix() for relative in assets for parent in Path(relative).parents if parent != Path(".")
    }
    if (
        "index.html" not in assets
        or actual_files != {*assets, MANIFEST_NAME}
        or actual_directories != declared_directories
    ):
        raise ValueError("client asset manifest closure differs")
    return assets


def _response(request: Request, asset: ClientAsset) -> Response:
    headers = {"ETag": asset.etag, "Content-Type": asset.media_type}
    if request.headers.get("if-none-match") == asset.etag:
        return Response(status_code=304, headers=headers)
    return Response(asset.data, headers=headers)


def create_vs01_web_app(archive_root: Path, web_root: Path) -> FastAPI:
    projection = compile_vs01_study_workspace(archive_root)
    workspace = canonical_workspace_projection_bytes(projection)
    base = read_t06_page_asset(archive_root, "base")
    degraded = read_t06_page_asset(archive_root, "degraded")
    assets = _client_assets(web_root)
    app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None, redirect_slashes=False)
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=["127.0.0.1", "localhost"])

    async def _secure(request: Request, call_next: Any) -> Response:
        try:
            response = await call_next(request)
        except Exception:
            response = Response("Internal server error", status_code=500, media_type="text/plain")
        response.headers.update(SECURITY_HEADERS)
        return response

    app.middleware("http")(_secure)

    frozen = {
        "/api/v1/vs01/john-1-5/workspace": ClientAsset("workspace", "application/json", workspace, _etag(workspace)),
        "/api/v1/vs01/john-1-5/page/base.png": ClientAsset("base", "image/png", base, _etag(base)),
        "/api/v1/vs01/john-1-5/page/degraded.png": ClientAsset("degraded", "image/png", degraded, _etag(degraded)),
    }
    for route, asset in frozen.items():
        app.add_api_route(route, _asset_endpoint(asset), methods=["GET"], include_in_schema=False)
    app.add_api_route("/", _asset_endpoint(assets["index.html"]), methods=["GET"], include_in_schema=False)
    for relative, asset in assets.items():
        if relative != "index.html":
            app.add_api_route(f"/{relative}", _asset_endpoint(asset), methods=["GET"], include_in_schema=False)
    return app


def _etag(data: bytes) -> str:
    return f'"{hashlib.sha256(data).hexdigest()}"'


def _asset_endpoint(asset: ClientAsset) -> Any:
    async def endpoint(request: Request) -> Response:
        return _response(request, asset)

    return endpoint


def run_vs01_web(port: int) -> None:
    app = create_vs01_web_app(ARCHIVE_ROOT, WEB_ROOT)
    uvicorn.run(app, host="127.0.0.1", port=port, workers=1, reload=False, access_log=False)
