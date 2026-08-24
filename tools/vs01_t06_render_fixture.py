#!/usr/bin/env python3
"""Render the one frozen VS01-T06 synthetic John 1:5 fixture."""

from __future__ import annotations

import argparse
import binascii
import hashlib
import json
import struct
import zlib
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFilter, ImageFont
from PIL import __version__ as pillow_version

SPEC_SHA256 = "dd76d124b0ab9c42cb3551e1afd5a9e0326ac402977ae3f4625d9092fd80b285"
RENDERER_SHA256 = "3ac7df8910bf4ea6a630a8f5e222483541121458620a80edf5bab20d067623de"
REGULAR_SHA256 = "e5a4ee6a3d87bb9024796be390c6771e2a0eb1883dae25effaf57ca01668e24b"
ITALIC_SHA256 = "9d2950a8f1da66e21502c35d646a1d2148e79f9ea43fd2158cf02f5232e7f430"
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
WIDTH, HEIGHT = 1600, 2200


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _read_json(path: Path, expected_sha: str) -> dict[str, Any]:
    data = path.read_bytes()
    if _sha256(data) != expected_sha:
        raise ValueError(f"authority hash differs: {path.name}")
    value = json.loads(data)
    if not isinstance(value, dict):
        raise ValueError(f"authority is not an object: {path.name}")
    return value


def _font(path: Path, size: int, expected_sha: str) -> ImageFont.FreeTypeFont:
    if path.is_symlink() or not path.is_file() or _sha256(path.read_bytes()) != expected_sha:
        raise ValueError(f"font authority differs: {path.name}")
    return ImageFont.truetype(str(path), size=size, layout_engine=ImageFont.Layout.BASIC)


def _rgb(value: str) -> tuple[int, int, int]:
    return tuple(bytes.fromhex(value.removeprefix("#")))  # type: ignore[return-value]


def _chunk(kind: bytes, payload: bytes) -> bytes:
    body = kind + payload
    return struct.pack(">I", len(payload)) + body + struct.pack(">I", binascii.crc32(body) & 0xFFFFFFFF)


def canonical_png_bytes(image: Image.Image) -> bytes:
    if image.mode != "RGB" or image.size != (WIDTH, HEIGHT):
        raise ValueError("authority raster must be 1600x2200 RGB")
    pixels = image.tobytes()
    scanlines = b"".join(b"\x00" + pixels[row * WIDTH * 3 : (row + 1) * WIDTH * 3] for row in range(HEIGHT))
    compressor = zlib.compressobj(9, zlib.DEFLATED, 15, 9, zlib.Z_DEFAULT_STRATEGY)
    compressed = compressor.compress(scanlines) + compressor.flush()
    return b"".join(
        (
            PNG_SIGNATURE,
            _chunk(b"IHDR", struct.pack(">IIBBBBB", WIDTH, HEIGHT, 8, 2, 0, 0, 0)),
            _chunk(b"sRGB", b"\x00"),
            _chunk(b"pHYs", struct.pack(">IIB", 7874, 7874, 1)),
            _chunk(b"IDAT", compressed),
            _chunk(b"IEND", b""),
        )
    )


def inspect_png(data: bytes, expected_pixels: bytes) -> dict[str, Any]:
    if not data.startswith(PNG_SIGNATURE):
        raise ValueError("PNG signature differs")
    offset, chunks, payloads = len(PNG_SIGNATURE), [], []
    while offset < len(data):
        length = struct.unpack(">I", data[offset : offset + 4])[0]
        kind = data[offset + 4 : offset + 8]
        payload = data[offset + 8 : offset + 8 + length]
        crc = struct.unpack(">I", data[offset + 8 + length : offset + 12 + length])[0]
        if binascii.crc32(kind + payload) & 0xFFFFFFFF != crc:
            raise ValueError("PNG CRC differs")
        chunks.append(kind.decode("ascii"))
        payloads.append(payload)
        offset += length + 12
    ihdr = struct.unpack(">IIBBBBB", payloads[0])
    scanlines = zlib.decompress(payloads[3])
    decoded = b"".join(scanlines[row * (WIDTH * 3 + 1) + 1 : (row + 1) * (WIDTH * 3 + 1)] for row in range(HEIGHT))
    checks = (
        offset == len(data),
        chunks == ["IHDR", "sRGB", "pHYs", "IDAT", "IEND"],
        ihdr == (WIDTH, HEIGHT, 8, 2, 0, 0, 0),
        payloads[1] == b"\x00",
        payloads[2] == struct.pack(">IIB", 7874, 7874, 1),
        payloads[4] == b"",
        len(scanlines) == HEIGHT * (WIDTH * 3 + 1),
        all(scanlines[row * (WIDTH * 3 + 1)] == 0 for row in range(HEIGHT)),
        decoded == expected_pixels,
    )
    if not all(checks):
        raise ValueError("canonical PNG self-inspection failed")
    return {"chunks": chunks, "crc_valid": True, "scanlines_match_rgb": True, "filter": 0}


def _glyphs(font: ImageFont.FreeTypeFont, text: str) -> None:
    missing = bytes(font.getmask("\u0378"))
    for character in set(text):
        if character.isspace():
            continue
        mask = bytes(font.getmask(character))
        if not mask or mask == missing:
            raise ValueError(f"font lacks glyph U+{ord(character):04X}")


def _inside(inner: tuple[int, int, int, int], xywh: list[int]) -> bool:
    x, y, width, height = xywh
    return inner[0] >= x and inner[1] >= y and inner[2] <= x + width and inner[3] <= y + height


def _draw_text(
    image: Image.Image,
    region: dict[str, Any],
    style: dict[str, Any],
    text: str,
    position: list[int],
    font: ImageFont.FreeTypeFont,
) -> tuple[int, int, int, int]:
    _glyphs(font, text)
    draw = ImageDraw.Draw(image)
    bbox = draw.textbbox(tuple(position), text, font=font, anchor=style["anchor"])
    if not _inside(bbox, region["pixel_bbox_xywh"]):
        raise ValueError(f"text ink exceeds frozen region {region['region_id']}: {bbox}")
    draw.text(tuple(position), text, font=font, fill=_rgb(style["fill_rgb"]), anchor=style["anchor"])
    return bbox


def _draw_annotation(
    image: Image.Image, region: dict[str, Any], style: dict[str, Any], font: ImageFont.FreeTypeFont
) -> tuple[int, int, int, int]:
    text, position = region["text"], style["draw_position_px"]
    _glyphs(font, text)
    mask = Image.new("L", image.size, 0)
    ImageDraw.Draw(mask).text(tuple(position), text, font=font, fill=255, anchor=style["anchor"])
    angle = -float(style["rotation_degrees_clockwise"])
    mask = mask.rotate(angle, resample=Image.Resampling.BICUBIC, center=tuple(style["rotation_center_px"]))
    bbox = mask.getbbox()
    if bbox is None or not _inside(bbox, region["pixel_bbox_xywh"]):
        raise ValueError(f"annotation ink exceeds frozen region: {bbox}")
    color = Image.new("RGB", image.size, _rgb(style["fill_rgb"]))
    image.paste(color, (0, 0), mask)
    return bbox


def _combined_bbox(boxes: list[tuple[int, int, int, int]]) -> tuple[int, int, int, int]:
    return (
        min(box[0] for box in boxes),
        min(box[1] for box in boxes),
        max(box[2] for box in boxes),
        max(box[3] for box in boxes),
    )


def _render_region(
    image: Image.Image,
    region: dict[str, Any],
    style: dict[str, Any],
    regular: Path,
    italic: Path,
) -> tuple[int, int, int, int]:
    italic_face = style["font_face"] == "Italic"
    font_path = italic if italic_face else regular
    font_sha = ITALIC_SHA256 if italic_face else REGULAR_SHA256
    font = _font(font_path, style["font_size_px"], font_sha)
    if region["region_id"] == "r_note":
        rect = style["background_rect_xywh"]
        ImageDraw.Draw(image).rectangle(
            (rect[0], rect[1], rect[0] + rect[2] - 1, rect[1] + rect[3] - 1),
            fill=_rgb(style["background_rgb"]),
            outline=_rgb(style["border_rgb"]),
            width=2,
        )
    if region["region_id"] == "r_annotation":
        return _draw_annotation(image, region, style, font)
    lines = style.get("draw_lines")
    if lines is None:
        lines = [{"position_px": style["draw_position_px"], "text": region["text"]}]
    boxes = [_draw_text(image, region, style, line["text"], line["position_px"], font) for line in lines]
    return _combined_bbox(boxes)


def _render_base(spec: dict[str, Any], regular: Path, italic: Path) -> tuple[Image.Image, dict[str, Any]]:
    scene, boxes = spec["scene"], {}
    image = Image.new("RGB", (WIDTH, HEIGHT), _rgb(scene["canvas"]["background_rgb"]))
    graphic = scene["display_only_graphics"][0]
    ImageDraw.Draw(image).line(
        (tuple(graphic["start_px"]), tuple(graphic["end_px"])),
        fill=_rgb(graphic["stroke_rgb"]),
        width=2,
    )
    for region in scene["regions"]:
        style = scene["styles"][region["style_id"]]
        boxes[region["region_id"]] = _render_region(image, region, style, regular, italic)
    if len(scene["regions"]) != 7 or len(boxes) != 7:
        raise ValueError("frozen region count differs")
    return image, boxes


def _degrade(base: Image.Image, spec: dict[str, Any], regular: Path) -> Image.Image:
    degraded, scene = base.copy(), spec["scene"]
    operation, glare = scene["views"][1]["operations"]
    style = scene["styles"]["style_canonical"]
    line = style["draw_lines"][operation["target_line_index_zero_based"]]
    start, end = operation["target_character_range_half_open"]
    font = _font(regular, style["font_size_px"], REGULAR_SHA256)
    draw = ImageDraw.Draw(degraded)
    prefix, target = line["text"][:start], line["text"][start:end]
    x = line["position_px"][0] + round(draw.textlength(prefix, font=font))
    bbox = draw.textbbox((x, line["position_px"][1]), target, font=font, anchor=style["anchor"])
    region = next(item for item in scene["regions"] if item["region_id"] == operation["region_id"])["pixel_bbox_xywh"]
    rx, ry, rw, rh = region
    expand = 14
    mask_bbox = (
        max(rx, bbox[0] - expand),
        max(ry, bbox[1] - expand),
        min(rx + rw, bbox[2] + expand),
        min(ry + rh, bbox[3] + expand),
    )
    crop = degraded.crop(mask_bbox).filter(ImageFilter.GaussianBlur(radius=float(operation["sigma"])))
    degraded.paste(crop, mask_bbox)
    gx, gy, gw, gh = glare["pixel_bbox_xywh"]
    ImageDraw.Draw(degraded).rectangle((gx, gy, gx + gw - 1, gy + gh - 1), fill=_rgb(glare["fill_rgb"]))
    return degraded


def _write_output(path: Path, image: Image.Image) -> dict[str, Any]:
    data = canonical_png_bytes(image)
    inspection = inspect_png(data, image.tobytes())
    path.write_bytes(data)
    if path.read_bytes() != data:
        raise ValueError("written PNG bytes differ")
    return {"path": path.name, "sha256": _sha256(data), "byte_count": len(data), "inspection": inspection}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--spec", required=True, type=Path)
    parser.add_argument("--regular-font", required=True, type=Path)
    parser.add_argument("--italic-font", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--renderer-authority", required=True, type=Path)
    args = parser.parse_args()
    spec = _read_json(args.spec, SPEC_SHA256)
    renderer = _read_json(args.renderer_authority, RENDERER_SHA256)
    if pillow_version != "12.3.0" or renderer["platform"] != "linux/amd64":
        raise ValueError("runtime renderer differs from frozen authority")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    base, ink_boxes = _render_base(spec, args.regular_font, args.italic_font)
    degraded = _degrade(base, spec, args.regular_font)
    outputs = [
        _write_output(args.output_dir / "john-1-5-base-page.png", base),
        _write_output(args.output_dir / "john-1-5-degraded-illegibility-v1.png", degraded),
    ]
    receipt = {
        "schema_version": "1.0",
        "scene_spec_identity": spec["scene_spec_identity"],
        "spec_sha256": SPEC_SHA256,
        "renderer_authority_sha256": RENDERER_SHA256,
        "font_sha256": {"regular": REGULAR_SHA256, "italic": ITALIC_SHA256},
        "outputs": outputs,
        "ink_bboxes": ink_boxes,
        "glyphs_verified": True,
        "ocr_invocations": 0,
        "vlm_invocations": 0,
        "model_invocations": 0,
    }
    receipt_path = args.output_dir / "john-1-5-render-receipt.json"
    receipt_path.write_bytes(
        json.dumps(receipt, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode() + b"\n"
    )
    print(json.dumps(receipt, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
