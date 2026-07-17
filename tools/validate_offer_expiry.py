#!/usr/bin/env python3
import argparse
import json
import re
import subprocess
import sys
from datetime import timedelta, timezone
from pathlib import Path

import sync_site_content as sync

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "reports" / "offer-expiry-dry-run.md"


def parse_args():
    parser = argparse.ArgumentParser(description="Validate the Lifetime Premium expiry contract without changing files.")
    parser.add_argument("--write-report", action="store_true", help="Write the local dry-run report.")
    parser.add_argument(
        "--check-worktree",
        action="store_true",
        help="Confirm a workflow run changed only offer HTML and sitemap.xml.",
    )
    return parser.parse_args()


def source_or_desired(path, desired):
    return desired.get(path, path.read_text(encoding="utf-8"))


def offer_html_paths():
    paths = []
    for path in sorted(ROOT.rglob("*.html")):
        if ".git" in path.parts:
            continue
        text = path.read_text(encoding="utf-8")
        if "data-offer-copy" in text:
            paths.append(path)
    return paths


def validate_contract():
    facts = json.loads(sync.FACTS_PATH.read_text(encoding="utf-8"))
    expiry = sync.parsed_time(facts["founding_offer"]["expires_at"])
    before = expiry - timedelta(seconds=1)
    after = expiry
    before_state, before_desired = sync.desired_files(before)
    after_state, after_desired = sync.desired_files(after)

    errors = []
    if before_state != "active":
        errors.append(f"Expected active immediately before expiry, got {before_state}.")
    if after_state != "expired":
        errors.append(f"Expected expired at the expiry instant, got {after_state}.")

    offer_paths = offer_html_paths()
    changed = []
    for path in offer_paths:
        active_html = source_or_desired(path, before_desired)
        expired_html = source_or_desired(path, after_desired)
        if active_html == expired_html:
            errors.append(f"Offer copy did not change in {path.relative_to(ROOT)}.")
            continue
        changed.append(path)
        if re.search(r'data-offer-copy="active\.', expired_html):
            errors.append(f"Active offer key remains after expiry in {path.relative_to(ROOT)}.")
        if not re.search(r'data-offer-copy="expired\.', expired_html):
            errors.append(f"Expired offer key is missing after expiry in {path.relative_to(ROOT)}.")
        if "offer-active-only" in expired_html or "offer-expired-only" in expired_html:
            errors.append(f"Conflicting static offer variants remain in {path.relative_to(ROOT)}.")

    if not offer_paths:
        errors.append("No crawler-visible offer pages were found.")
    if set(changed) != set(offer_paths):
        errors.append("Not every crawler-visible offer page switches state at expiry.")

    return {
        "expiry": expiry,
        "before": before,
        "after": after,
        "offer_paths": offer_paths,
        "changed": changed,
        "errors": errors,
    }


def check_worktree(allowed_html):
    result = subprocess.run(
        ["git", "diff", "--name-only"],
        cwd=ROOT,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    changed = {line.strip() for line in result.stdout.splitlines() if line.strip()}
    allowed = {path.relative_to(ROOT).as_posix() for path in allowed_html}
    allowed.add("sitemap.xml")
    unexpected = sorted(changed - allowed)
    if unexpected:
        raise RuntimeError("Unexpected files changed by offer workflow: " + ", ".join(unexpected))
    print(f"offer workflow changed only allowed files ({len(changed)} files)")


def write_report(result):
    expiry_utc = result["expiry"].astimezone(timezone.utc)
    lines = [
        "# Lifetime Premium Offer Expiry Dry Run",
        "",
        f"Expiry configured: `{result['expiry'].isoformat()}`",
        f"Expiry in UTC: `{expiry_utc.isoformat()}`",
        f"Before test: `{result['before'].isoformat()}` -> active",
        f"At-expiry test: `{result['after'].isoformat()}` -> expired",
        "",
        "## Assertions",
        "",
        "- The offer is active one second before expiry.",
        "- The offer is expired at the configured expiry instant.",
        "- Every crawler-visible offer page changes from active keys to expired keys.",
        "- No page exposes active and expired static variants together.",
        "- The test does not write website files.",
        "",
        f"Crawler-visible pages switched: {len(result['changed'])}",
        "",
    ]
    for path in result["changed"]:
        lines.append(f"- `{path.relative_to(ROOT).as_posix()}`")
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    args = parse_args()
    result = validate_contract()
    if result["errors"]:
        for error in result["errors"]:
            print(f"FAIL: {error}")
        return 1
    if args.check_worktree:
        check_worktree(result["offer_paths"])
    if args.write_report:
        write_report(result)
        print(f"wrote {REPORT.relative_to(ROOT)}")
    print(f"offer expiry contract passed for {len(result['changed'])} crawler-visible pages")
    return 0


if __name__ == "__main__":
    sys.exit(main())
