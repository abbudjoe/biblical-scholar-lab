from __future__ import annotations

import asyncio
import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest
from test_vs01_study_workspace import synthetic_archive as _synthetic_archive

import bsl.interfaces.cli as cli
from bsl.interfaces import vs01_web

ROOT = Path(__file__).parents[1]
DIST = ROOT / "web/dist"
WORKSPACE = (ROOT / "fixtures/VS01-T09/john-1-5-study-workspace-projection.json").read_bytes().removesuffix(b"\n")
BASE = (ROOT / "fixtures/VS01-T06/john-1-5-base-page.png").read_bytes()
DEGRADED = (ROOT / "fixtures/VS01-T06/john-1-5-degraded-illegibility-v1.png").read_bytes()


def request(
    app: Any, path: str, method: str = "GET", headers: dict[str, str] | None = None
) -> tuple[int, dict[str, str], bytes]:
    messages: list[dict[str, Any]] = []
    sent = False

    async def receive() -> dict[str, Any]:
        nonlocal sent
        if not sent:
            sent = True
            return {"type": "http.request", "body": b"", "more_body": False}
        return {"type": "http.disconnect"}

    async def send(message: dict[str, Any]) -> None:
        messages.append(message)

    raw_headers = [(key.lower().encode(), value.encode()) for key, value in (headers or {}).items()]
    if not any(key == b"host" for key, _ in raw_headers):
        raw_headers.append((b"host", b"127.0.0.1"))
    scope = {
        "type": "http",
        "asgi": {"version": "3.0"},
        "http_version": "1.1",
        "method": method,
        "scheme": "http",
        "path": path,
        "raw_path": path.encode(),
        "query_string": b"",
        "headers": raw_headers,
        "client": ("127.0.0.1", 50000),
        "server": ("127.0.0.1", 4173),
        "root_path": "",
    }
    asyncio.run(app(scope, receive, send))
    start = next(item for item in messages if item["type"] == "http.response.start")
    response_headers = {key.decode().lower(): value.decode() for key, value in start["headers"]}
    body = b"".join(item.get("body", b"") for item in messages if item["type"] == "http.response.body")
    return start["status"], response_headers, body


@pytest.fixture
def synthetic_archive(tmp_path: Path) -> Path:
    return _synthetic_archive.__wrapped__(tmp_path)


@pytest.fixture
def app(synthetic_archive: Path) -> Any:
    return vs01_web.create_vs01_web_app(synthetic_archive, DIST)


@pytest.mark.parametrize(
    ("path", "expected", "content_type"),
    (
        ("/api/v1/vs01/john-1-5/workspace", WORKSPACE, "application/json"),
        ("/api/v1/vs01/john-1-5/page/base.png", BASE, "image/png"),
        ("/api/v1/vs01/john-1-5/page/degraded.png", DEGRADED, "image/png"),
    ),
)
def test_exact_api_bytes_etags_headers_and_conditional_get(
    app: Any, path: str, expected: bytes, content_type: str
) -> None:
    status, headers, body = request(app, path)
    etag = f'"{hashlib.sha256(expected).hexdigest()}"'
    assert (status, body, headers["content-type"], headers["etag"]) == (200, expected, content_type, etag)
    assert {key: headers[key] for key in (name.lower() for name in vs01_web.SECURITY_HEADERS)} == {
        key.lower(): value for key, value in vs01_web.SECURITY_HEADERS.items()
    }
    status, headers, body = request(app, path, headers={"If-None-Match": etag})
    assert (status, body, headers["etag"]) == (304, b"", etag)


def test_static_manifest_routes_and_absent_surfaces(app: Any) -> None:
    manifest = json.loads((DIST / "asset-manifest.json").read_bytes())
    for asset in manifest["assets"]:
        path = "/" if asset["path"] == "index.html" else f"/{asset['path']}"
        status, headers, body = request(app, path)
        assert (status, len(body), hashlib.sha256(body).hexdigest()) == (200, asset["byte_count"], asset["sha256"])
        assert headers["content-type"] == asset["media_type"]
    static_path = next(f"/{asset['path']}" for asset in manifest["assets"] if asset["path"] != "index.html")
    status, headers, _ = request(app, f"{static_path}/")
    assert status == 404 and status not in {301, 302, 307, 308} and "location" not in headers
    for path in (
        "/docs /redoc /openapi.json /asset-manifest.json /upload /model /database /assets /../index.html "  # noqa: SIM905
        "/%2e%2e/index.html /assets/%2e%2e/index.html /missing".split()
    ):
        assert request(app, path)[0] == 404
    assert request(app, "/api/v1/vs01/john-1-5/workspace", "POST")[0] == 405
    assert request(app, "/", "POST")[0] == 405
    assert "access-control-allow-origin" not in request(app, "/")[1]


@pytest.mark.parametrize(
    "path",
    "/api/v1/vs01/john-1-5/workspace/ /api/v1/vs01/john-1-5/page/base.png/ "  # noqa: SIM905
    "/api/v1/vs01/john-1-5/page/degraded.png/".split(),
)
def test_scholarly_routes_reject_trailing_slashes_without_redirect(app: Any, path: str) -> None:
    status, headers, _ = request(app, path)
    assert status == 404
    assert status not in {301, 302, 307, 308}
    assert "location" not in headers


def test_host_rejection_and_security_on_errors(app: Any) -> None:
    status, headers, body = request(app, "/", headers={"Host": "attacker.example"})
    assert status == 400 and b"Invalid host" in body
    assert headers["x-content-type-options"] == "nosniff"
    assert request(app, "/missing")[1]["x-frame-options"] == "DENY"


@pytest.mark.parametrize(
    "case",
    "changed missing missing-manifest symlink extra extra-directory manifest-extra unsafe route-pattern self duplicate "  # noqa: SIM905
    "directory nonregular-extra".split(),
)
def test_manifest_authority_fails_closed(tmp_path: Path, synthetic_archive: Path, case: str) -> None:
    web = tmp_path / "dist"
    shutil.copytree(DIST, web)
    manifest_path = web / "asset-manifest.json"
    manifest = json.loads(manifest_path.read_bytes())
    first = web / manifest["assets"][1]["path"]
    if case == "changed":
        first.write_bytes(first.read_bytes() + b"changed")
    elif case == "missing":
        first.unlink()
    elif case == "missing-manifest":
        manifest_path.unlink()
    elif case == "symlink":
        first.unlink()
        first.symlink_to(web / "index.html")
    elif case == "extra":
        (web / "extra.js").write_text("extra")
    elif case == "extra-directory":
        (web / "undeclared").mkdir()
    elif case == "manifest-extra":
        manifest["unexpected"] = True
        manifest_path.write_text(json.dumps(manifest))
    elif case == "unsafe":
        manifest["assets"][0]["path"] = "../index.html"
        manifest_path.write_text(json.dumps(manifest))
    elif case == "route-pattern":
        manifest["assets"][0]["path"] = "assets/{path}.js"
        manifest_path.write_text(json.dumps(manifest))
    elif case == "self":
        manifest["assets"][0]["path"] = "asset-manifest.json"
        manifest_path.write_text(json.dumps(manifest))
    elif case == "duplicate":
        manifest["assets"].append(manifest["assets"][0])
        manifest_path.write_text(json.dumps(manifest))
    elif case == "nonregular-extra":
        os.mkfifo(web / "undeclared-pipe")
    else:
        manifest["assets"][0]["path"] = "assets"
        manifest_path.write_text(json.dumps(manifest))
    with pytest.raises(ValueError, match="client asset"):
        vs01_web.create_vs01_web_app(synthetic_archive, web)


def test_mutable_authority_fails_before_service(synthetic_archive: Path) -> None:
    target = synthetic_archive / "snapshots/benchmark/vs01-b08-runtime-pair/reference-screening.json"
    target.chmod(0o644)
    with pytest.raises(ValueError, match="immutable regular file"):
        vs01_web.create_vs01_web_app(synthetic_archive, DIST)


@pytest.mark.parametrize("case", "changed missing symlink nonregular noncanonical".split())  # noqa: SIM905
def test_broken_archive_authority_fails_before_service(synthetic_archive: Path, case: str) -> None:
    target = synthetic_archive / "snapshots/benchmark/vs01-b08-runtime-pair/reference-screening.json"
    target.chmod(0o644)
    if case == "changed":
        target.write_bytes(target.read_bytes() + b"changed")
    elif case == "missing":
        target.unlink()
    elif case == "symlink":
        target.unlink()
        target.symlink_to(synthetic_archive / "objects")
    elif case == "nonregular":
        target.unlink()
        target.mkdir()
    else:
        target.write_bytes(target.read_bytes() + b"\n")
        target.chmod(0o444)
    with pytest.raises(ValueError):
        vs01_web.create_vs01_web_app(synthetic_archive, DIST)


@pytest.mark.parametrize("port", ("1023", "65536", "abc"))
def test_cli_rejects_invalid_or_privileged_ports(port: str, capsys: pytest.CaptureFixture[str]) -> None:
    assert cli.main(["web", "vs01", "--port", port]) == 2
    assert json.loads(capsys.readouterr().out)["error"]["code"] == "INVALID_CLI_INPUT"


@pytest.mark.parametrize("option", ("--host", "--archive-root"))
def test_cli_exposes_no_host_or_archive_override(option: str, capsys: pytest.CaptureFixture[str]) -> None:
    assert cli.main(["web", "vs01", "--port", "4173", option, "changed"]) == 2
    assert json.loads(capsys.readouterr().out)["error"]["code"] == "INVALID_CLI_INPUT"


def test_cli_and_runner_use_only_fixed_loopback_parameters(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[Any] = []
    monkeypatch.setattr(cli, "run_vs01_web", lambda port: calls.append(port))
    assert cli.main(["web", "vs01", "--port", "4173"]) == 0 and calls == [4173]
    app = object()
    monkeypatch.setattr(vs01_web, "create_vs01_web_app", lambda archive, web: calls.append((archive, web)) or app)
    monkeypatch.setattr(vs01_web.uvicorn, "run", lambda *args, **kwargs: calls.append((args, kwargs)))
    vs01_web.run_vs01_web(4173)
    assert calls[-2] == (vs01_web.ARCHIVE_ROOT, vs01_web.WEB_ROOT)
    assert calls[-1] == (
        (app,),
        {"host": "127.0.0.1", "port": 4173, "workers": 1, "reload": False, "access_log": False},
    )


def test_cli_commands_keep_web_and_other_execution_subsystems_isolated() -> None:
    script = """
import sys

web_runtime = ("fastapi", "uvicorn", "bsl.interfaces.vs01_web", "bsl.application.vs01_study_workspace",
               "bsl.infrastructure.study_workspace_authority")
other_execution = ("bsl.application.john15_study_runtime", "bsl.application.source_acquisition",
                   "bsl.application.vs01_benchmark_scoring", "bsl.application.vs01_runtime_screening", "psycopg")
def assert_absent(names):
    loaded = tuple(sys.modules)
    assert not any(name == item or item.startswith(f"{name}.") for name in names for item in loaded)

import bsl.interfaces.cli as cli
assert_absent(web_runtime)
assert cli.main(["source", "plan", "--manifest", "/definitely-absent-vs01-t09b-manifest.json"]) == 2
assert_absent(web_runtime)
import bsl.interfaces.vs01_web as web
web.run_vs01_web = lambda port: None
assert cli.main(["web", "vs01", "--port", "4173"]) == 0
assert_absent(other_execution)
"""
    result = subprocess.run(
        [sys.executable, "-c", script],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
