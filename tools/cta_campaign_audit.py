#!/usr/bin/env python3
import argparse
import csv
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from seo_priority_pass import CAMPAIGNS, PAGES

ROOT = Path(__file__).resolve().parents[1]
INVENTORY = ROOT / "reports" / "app-store-cta-inventory.csv"
DESIGN = ROOT / "reports" / "app-store-cta-measurement.md"

HOMEPAGE_CAMPAIGNS = {
    "homepageTopBanner": "founding_home_top_banner",
    "homepageHero": "founding_home_hero",
    "mobileSticky": "founding_mobile_sticky",
    "freeLifetime": "founding_free_lifetime",
}

ANCHOR_RE = re.compile(r'<a\b(?=[^>]*\bdata-app-store-link\b)[^>]*>', re.I)
ATTR_RE = re.compile(r'([a-zA-Z_:][-a-zA-Z0-9_:.]*)="([^"]*)"')
SCRIPT_RE = re.compile(r'<script\b[^>]*\bsrc="([^"]+)"', re.I)


def attrs(tag):
    return {key.lower(): value for key, value in ATTR_RE.findall(tag)}


def config_campaigns():
    text = (ROOT / "site-config.js").read_text(encoding="utf-8")
    return dict(re.findall(r'^\s*([A-Za-z][A-Za-z0-9]*): campaignUrl\("([^"]+)"\)', text, re.M))


def parse_args():
    parser = argparse.ArgumentParser(description="Audit privacy-first App Store campaign links.")
    parser.add_argument("--check", action="store_true", help="Validate without rewriting reports.")
    return parser.parse_args()


def href_token(href):
    return parse_qs(urlparse(href).query).get("ct", [""])[0]


def audit():
    config = config_campaigns()
    rows = []
    errors = []
    for key, token in HOMEPAGE_CAMPAIGNS.items():
        if config.get(key) != token:
            errors.append(f"site-config.js: {key} does not resolve to {token}")
    for path, page in PAGES.items():
        expected_key, expected_token = CAMPAIGNS[page["campaign"]]
        if config.get(expected_key) != expected_token:
            errors.append(f"{path}: config key {expected_key} does not resolve to {expected_token}")
        html = (ROOT / path).read_text(encoding="utf-8")
        placements = set()
        for tag in ANCHOR_RE.findall(html):
            data = attrs(tag)
            placement = data.get("data-cta-placement")
            if not placement:
                continue
            campaign_key = data.get("data-app-store-campaign", "")
            token = href_token(data.get("href", ""))
            placements.add(placement)
            if campaign_key != expected_key:
                errors.append(f"{path} {placement}: expected campaign key {expected_key}, got {campaign_key or 'none'}")
            if token != expected_token:
                errors.append(f"{path} {placement}: expected static token {expected_token}, got {token or 'none'}")
            rows.append(
                {
                    "page": path,
                    "placement": placement,
                    "campaign_key": campaign_key,
                    "campaign_token": token,
                    "href": data.get("href", ""),
                }
            )
        missing = {"hero", "answer", "bottom"} - placements
        if missing:
            errors.append(f"{path}: missing measured CTA placements {', '.join(sorted(missing))}")

        for src in SCRIPT_RE.findall(html):
            if src.startswith(("http://", "https://", "//")):
                errors.append(f"{path}: external analytics/script source is not allowed: {src}")
    return rows, errors, config


def write_reports(rows, config):
    fields = ["page", "placement", "campaign_key", "campaign_token", "href"]
    with INVENTORY.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    lines = [
        "# Privacy-First App Store CTA Measurement",
        "",
        f"Generated: {datetime.now(timezone.utc).isoformat(timespec='seconds')}",
        "",
        "## What Is Implemented",
        "",
        "- Every homepage offer placement uses a distinct Apple campaign link.",
        "- Every priority SEO page uses its own Apple campaign token.",
        "- Hero, answer and bottom CTAs are labelled in HTML so placement can be audited.",
        "- JavaScript resolves each named campaign key to the same token used in crawler-visible HTML.",
        "- No third-party analytics, tracking pixel, cookie, fingerprint or click beacon is added.",
        "",
        "## Data Flow",
        "",
        "1. The website displays an ordinary App Store link with an Apple `ct` campaign token.",
        "2. No measurement request is sent when the page loads.",
        "3. Apple receives the campaign token only when the visitor chooses the App Store link.",
        "4. Results are reviewed in App Store Connect when Apple provides enough campaign data.",
        "",
        "## Campaign Scope",
        "",
        "Homepage placements are measured separately. Priority SEO pages are measured by page, not by individual button. This keeps reporting understandable and avoids creating dozens of low-volume campaigns.",
        "",
        "## Limits",
        "",
        "- App Store campaign data can compare attributed App Store activity, but it cannot provide website click-through rate on its own.",
        "- Website CTR requires aggregate first-party click counts. No such endpoint is added in this pass.",
        "- Do not infer performance from campaigns that do not meet Apple reporting thresholds.",
        "",
        "## Decision Rule",
        "",
        "Keep each campaign unchanged for at least 28 days. Compare matched time periods. Change one major page element at a time, and do not claim a conversion improvement without enough attributed activity.",
        "",
        f"Audited priority CTA links: {len(rows)}",
        f"Configured campaign keys: {len(config)}",
    ]
    DESIGN.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    args = parse_args()
    rows, errors, config = audit()
    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        return 1
    if not args.check:
        write_reports(rows, config)
    print(f"CTA campaign audit passed ({len(rows)} measured links)")
    if not args.check:
        print(f"wrote {INVENTORY.relative_to(ROOT)}")
        print(f"wrote {DESIGN.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
