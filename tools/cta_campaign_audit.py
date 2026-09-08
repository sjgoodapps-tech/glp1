#!/usr/bin/env python3
import argparse
import csv
import json
import re
import sys
from html import unescape
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
    return {key.lower(): unescape(value) for key, value in ATTR_RE.findall(tag)}


def config_campaigns():
    text = (ROOT / "site-config.js").read_text(encoding="utf-8")
    return dict(re.findall(r'^\s*([A-Za-z][A-Za-z0-9]*): campaignUrl\("([^"]+)"\)', text, re.M))


def parse_args():
    parser = argparse.ArgumentParser(description="Audit privacy-first App Store campaign links.")
    parser.add_argument("--check", action="store_true", help="Validate without rewriting reports.")
    parser.add_argument("--allow-unconfigured", action="store_true", help="Check link wiring only; does not certify campaign attribution.")
    return parser.parse_args()


def href_token(href):
    return parse_qs(urlparse(href).query).get("ct", [""])[0]


def audit(allow_unconfigured=False):
    config = config_campaigns()
    rows = []
    errors = []
    provider = json.loads((ROOT / "data/product-facts.json").read_text())["app_store_campaign"]["provider_token"]
    if not provider and not allow_unconfigured:
        errors.append("Campaign attribution NOT READY: add Apple's provider token to data/product-facts.json, then run sync_site_content.py")
    for file in ROOT.rglob("*.html"):
        for tag in ANCHOR_RE.findall(file.read_text(encoding="utf-8")):
            href = attrs(tag).get("href", "")
            url = urlparse(href)
            query = parse_qs(url.query)
            if url.scheme != "https" or url.hostname != "apps.apple.com" or "id6761775005" not in url.path:
                errors.append(f"{file.relative_to(ROOT)}: unexpected App Store destination")
            if not query.get("ct"):
                errors.append(f"{file.relative_to(ROOT)}: missing static campaign name")
            if provider and (query.get("pt") != [str(provider)] or query.get("mt") != ["8"]):
                errors.append(f"{file.relative_to(ROOT)}: provider/media token drift")
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
                errors.append(f"{path}: missing labelled CTA placements {', '.join(sorted(missing))}")

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
        "- Campaign names are configured. Attribution is NOT ready until an Apple-generated provider token is supplied and the strict audit passes.",
        "- Every priority SEO page uses its own Apple campaign token.",
        "- Hero, answer and bottom CTAs are labelled in HTML so placement can be audited.",
        "- JavaScript resolves each named campaign key to the same token used in crawler-visible HTML.",
        "- No third-party analytics, tracking pixel, cookie, fingerprint or click beacon is added.",
        "",
        "## Data Flow",
        "",
        "1. The website displays ordinary App Store links. Apple requires both `ct` and its generated `pt` provider token for campaign attribution.",
        "2. No measurement request is sent when the page loads.",
        "3. Apple receives the campaign token only when the visitor chooses the App Store link.",
        "4. Results are reviewed in App Store Connect when Apple provides enough campaign data.",
        "",
        "## Campaign Scope",
        "",
        "Homepage placements have separate campaign names. Priority SEO pages use page-level names. These labels do not prove that any downloads have been measured.",
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
    rows, errors, config = audit(args.allow_unconfigured)
    if not args.check:
        write_reports(rows, config)
    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        return 1
    print(f"CTA link wiring passed ({len(rows)} priority links; no download measurement is claimed)")
    if args.allow_unconfigured:
        print("Attribution readiness was not certified. Run without --allow-unconfigured before claiming campaign reporting works.")
    if not args.check:
        print(f"wrote {INVENTORY.relative_to(ROOT)}")
        print(f"wrote {DESIGN.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
