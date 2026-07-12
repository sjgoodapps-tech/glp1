#!/usr/bin/env python3
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data" / "screenshot-manifest.json"
OUT = ROOT / "reports" / "image-pipeline-report.md"
WIDTHS = [360, 720, 1080]
HOMEPAGE_WIDTHS = [480, 768, 1080, 1440]
HOMEPAGE_SOURCES = {
    "hero": "assets/en-hero-sales-wow.png",
    "setup": "assets/setup-pair.png",
    "dashboard": "assets/en-screen-dashboard.png",
    "photos-export": "assets/en-screen-photos-export.png",
    "advanced-graphs": "assets/en-screen-advanced-graphs.png",
    "projections": "assets/en-screen-projections.png",
    "quick-logging": "assets/en-screen-quick-logging.png",
    "global-coverage": "assets/en-screen-global-coverage.png",
    "medication-coverage": "assets/en-screen-medication-coverage.png",
}


def run(cmd):
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True, ""
    except (subprocess.CalledProcessError, FileNotFoundError) as exc:
        return False, str(exc)


def build_homepage_variants(lines):
    try:
        from PIL import Image
    except ImportError:
        lines.append("- homepage variants: Pillow is not available; no WebP/AVIF files generated")
        return 0

    out_dir = ROOT / "assets" / "responsive"
    out_dir.mkdir(parents=True, exist_ok=True)
    converted = 0
    for name, source_name in HOMEPAGE_SOURCES.items():
        source = ROOT / source_name
        if not source.exists():
            lines.append(f"- homepage `{name}`: source missing")
            continue
        with Image.open(source) as image:
            image = image.convert("RGB")
            for width in HOMEPAGE_WIDTHS:
                target_width = min(width, image.width)
                target_height = round(image.height * target_width / image.width)
                resized = image.resize((target_width, target_height), Image.Resampling.LANCZOS)
                base = out_dir / f"homepage-{name}-{target_width}"
                resized.save(base.with_suffix(".webp"), "WEBP", quality=82, method=6)
                resized.save(base.with_suffix(".avif"), "AVIF", quality=55, speed=6)
                converted += 1
    lines.append(f"- homepage variants: generated {converted * 2} WebP/AVIF files from {converted} resized source variants")
    return converted


def main():
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    has_sips = shutil.which("sips")
    has_cwebp = shutil.which("cwebp")
    has_avifenc = shutil.which("avifenc")
    lines = [
        "# Responsive Image Pipeline Report",
        "",
        "This script prepares the screenshot conversion map. It can convert files when raw screenshots are present and local encoders are available.",
        "",
        f"- sips available: {'yes' if has_sips else 'no'}",
        f"- cwebp available: {'yes' if has_cwebp else 'no'}",
        f"- avifenc available: {'yes' if has_avifenc else 'no'}",
        "",
        "## Slots",
        "",
    ]
    converted = 0
    missing = 0
    for slot in data["slots"]:
        raw = ROOT / slot["source_raw_filename_placeholder"]
        lines.append(f"- `{slot['slot']}`")
        lines.append(f"  - raw: `{slot['source_raw_filename_placeholder']}`")
        lines.append(f"  - webp: `{slot['target_webp_filename']}`")
        lines.append(f"  - avif: `{slot['target_avif_filename']}`")
        lines.append(f"  - alt: {slot['alt']}")
        if not raw.exists():
            missing += 1
            lines.append("  - status: waiting for screenshot")
            continue
        for width in WIDTHS:
            base = ROOT / "assets" / "screens" / f"{slot['expected_filename']}-{width}"
            base.parent.mkdir(parents=True, exist_ok=True)
            tmp_png = base.with_suffix(".png")
            if has_sips:
                ok, detail = run(["sips", "-Z", str(width), str(raw), "--out", str(tmp_png)])
                if not ok:
                    lines.append(f"  - {width}px PNG resize failed: {detail}")
                    continue
            else:
                tmp_png.write_bytes(raw.read_bytes())
            if has_cwebp:
                run(["cwebp", "-quiet", str(tmp_png), "-o", str(base.with_suffix(".webp"))])
            if has_avifenc:
                run(["avifenc", "--quiet", str(tmp_png), str(base.with_suffix(".avif"))])
            converted += 1
        lines.append("  - status: processed available raw screenshot")
    build_homepage_variants(lines)
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"processed variants: {converted}")
    print(f"waiting for raw screenshots: {missing}")
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
