#!/usr/bin/env python3
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data" / "screenshot-manifest.json"
OUT = ROOT / "reports" / "image-pipeline-report.md"
SEO_WIDTHS = [360, 720, 1080, 1320]
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


def parse_args():
    parser = argparse.ArgumentParser(description="Build responsive GLPzy screenshot assets.")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--seo-only", action="store_true", help="Build priority SEO page assets only.")
    group.add_argument("--homepage-only", action="store_true", help="Build homepage assets only.")
    return parser.parse_args()


def pillow_image():
    try:
        from PIL import Image
    except ImportError:
        return None
    return Image


def save_variants(image_module, source, prefix, widths, lines):
    out_dir = ROOT / "assets" / "responsive"
    out_dir.mkdir(parents=True, exist_ok=True)
    generated = []
    with image_module.open(source) as opened:
        image = opened.convert("RGB")
        target_widths = sorted({min(width, image.width) for width in widths})
        for target_width in target_widths:
            target_height = round(image.height * target_width / image.width)
            resized = image.resize((target_width, target_height), image_module.Resampling.LANCZOS)
            base = out_dir / f"{prefix}-{target_width}"
            webp = base.with_suffix(".webp")
            avif = base.with_suffix(".avif")
            resized.save(webp, "WEBP", quality=80, method=6)
            resized.save(avif, "AVIF", quality=52, speed=6)
            generated.extend([webp, avif])
    total_bytes = sum(path.stat().st_size for path in generated)
    lines.append(
        f"- `{source.relative_to(ROOT)}` -> `{prefix}-*`: "
        f"{len(generated)} files, {total_bytes / 1024:.0f} KB total"
    )
    return generated


def build_homepage_variants(image_module, lines):
    lines.extend(["", "## Homepage Assets", ""])
    generated = []
    for name, source_name in HOMEPAGE_SOURCES.items():
        source = ROOT / source_name
        if not source.exists():
            lines.append(f"- `{source_name}`: source missing")
            continue
        generated.extend(
            save_variants(image_module, source, f"homepage-{name}", HOMEPAGE_WIDTHS, lines)
        )
    return generated


def build_seo_variants(image_module, data, lines):
    lines.extend(["", "## Priority SEO Assets", ""])
    generated = []
    source_names = sorted(
        set(data.get("source_assets", {}).values())
        | set(data.get("priority_page_hero_assets", {}).values())
    )
    for source_name in source_names:
        source = ROOT / source_name
        if not source.exists():
            lines.append(f"- `{source_name}`: source missing")
            continue
        prefix = f"seo-{source.stem}"
        generated.extend(save_variants(image_module, source, prefix, SEO_WIDTHS, lines))

    lines.extend(["", "## SEO Screenshot Slots", ""])
    for slot in data["slots"]:
        source_name = data.get("source_assets", {}).get(slot["slot"], "")
        lines.append(
            f"- `{slot['slot']}`: `{source_name}`; alt: {slot['alt']}"
        )
    return generated


def main():
    args = parse_args()
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    image_module = pillow_image()
    if image_module is None:
        print("Pillow with WebP and AVIF support is required.", file=sys.stderr)
        return 1

    lines = [
        "# Responsive Image Pipeline Report",
        "",
        "Generated from the source screenshot map in `data/screenshot-manifest.json`.",
        "Original PNG files remain as fallbacks and social-sharing images.",
    ]
    generated = []
    if not args.seo_only:
        generated.extend(build_homepage_variants(image_module, lines))
    if not args.homepage_only:
        generated.extend(build_seo_variants(image_module, data, lines))

    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"generated {len(generated)} responsive files")
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
