#!/usr/bin/env python3
import argparse
import json
import re
import sys
from datetime import datetime, timezone
from html import escape, unescape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FACTS_PATH = ROOT / "data" / "product-facts.json"
CONFIG_PATH = ROOT / "site-config.js"
PREFLIGHT_PATH = ROOT / "site-preflight.js"


def parse_args():
    parser = argparse.ArgumentParser(description="Sync crawler-visible product and offer copy.")
    parser.add_argument("--check", action="store_true", help="Report drift without writing files.")
    parser.add_argument("--at", help="Use an ISO date/time instead of the current time.")
    return parser.parse_args()


def parsed_time(value):
    if not value:
        return datetime.now(timezone.utc)
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)


def generated_block(text, name, declaration):
    pattern = re.compile(
        rf'(?P<start>  // generated:{re.escape(name)}:start\n).*?'
        rf'(?P<end>\n  // generated:{re.escape(name)}:end)',
        re.S,
    )
    match = pattern.search(text)
    if not match:
        raise RuntimeError(f"Missing generated block markers for {name}")
    return text[:match.start()] + match.group("start") + declaration + match.group("end") + text[match.end():]


def js_declaration(name, value):
    payload = json.dumps(value, ensure_ascii=False, indent=2)
    indented = "\n".join("  " + line for line in payload.splitlines())
    return f"  var {name} = {indented.lstrip()};"


def normalize_text(value):
    return re.sub(r"\s+", " ", unescape(re.sub(r"<[^>]+>", " ", value))).strip()


def replace_data_copy(text, attribute, values, state=None):
    pattern = re.compile(
        rf'(?P<open><(?P<tag>[a-z][a-z0-9]*)\b[^>]*\b{re.escape(attribute)}="(?P<key>[^"]+)"[^>]*>)'
        rf'(?P<body>.*?)</(?P=tag)>',
        re.S | re.I,
    )

    def repl(match):
        key = match.group("key")
        lookup_key = key
        if state and "." in key:
            suffix = key.split(".", 1)[1]
            if suffix in values.get(state, {}):
                lookup_key = f"{state}.{suffix}"

        value = values
        for part in lookup_key.split("."):
            if not isinstance(value, dict) or part not in value:
                return match.group(0)
            value = value[part]
        if not isinstance(value, str):
            return match.group(0)

        opening = match.group("open")
        if lookup_key != key:
            opening = opening.replace(f'{attribute}="{key}"', f'{attribute}="{lookup_key}"')

        # Keep deliberate inline links when their visible wording already matches.
        if "<" in match.group("body") and normalize_text(match.group("body")) == value:
            body = match.group("body")
        else:
            body = escape(value)
        return opening + body + f'</{match.group("tag")}>'

    return pattern.sub(repl, text)


def remove_inactive_offer_variants(text):
    text = re.sub(
        r'\s*<(?P<tag>[a-z][a-z0-9]*)\b[^>]*\bclass="[^"]*\boffer-expired-only\b[^"]*"[^>]*>.*?</(?P=tag)>',
        "",
        text,
        flags=re.S | re.I,
    )

    def clean_class(match):
        classes = [item for item in match.group(1).split() if item != "offer-active-only"]
        return f'class="{" ".join(classes)}"' if classes else ""

    text = re.sub(r'class="([^"]*\boffer-active-only\b[^"]*)"', clean_class, text, flags=re.I)
    return re.sub(r'\s+class=""', "", text)


def desired_files(now):
    facts = json.loads(FACTS_PATH.read_text(encoding="utf-8"))
    product_claims = facts["product_claims"]
    offer = facts["founding_offer"]
    expires_at = parsed_time(offer["expires_at"])
    state = "active" if now.astimezone(timezone.utc) < expires_at.astimezone(timezone.utc) else "expired"

    desired = {}
    config = CONFIG_PATH.read_text(encoding="utf-8")
    config = generated_block(config, "product-claims", js_declaration("productClaims", product_claims))
    config = generated_block(
        config,
        "founding-offer-copy",
        js_declaration("foundingOfferCopy", {"active": offer["active"], "expired": offer["expired"]}),
    )
    config = re.sub(
        r'(?P<prefix>expiresAt:\s*)"[^"]*"',
        rf'\g<prefix>"{offer["expires_at"]}"',
        config,
        count=1,
    )
    desired[CONFIG_PATH] = config

    preflight = PREFLIGHT_PATH.read_text(encoding="utf-8")
    preflight = re.sub(
        r'(?P<prefix>var expiresAt = )"[^"]*"',
        rf'\g<prefix>"{offer["expires_at"]}"',
        preflight,
        count=1,
    )
    desired[PREFLIGHT_PATH] = preflight

    offer_copy = {"active": offer["active"], "expired": offer["expired"]}
    for path in sorted(ROOT.rglob("*.html")):
        if ".git" in path.parts:
            continue
        html = path.read_text(encoding="utf-8")
        updated = replace_data_copy(html, "data-claim-copy", product_claims)
        if "data-offer-copy" in updated or "offer-expired-only" in updated or "offer-active-only" in updated:
            updated = remove_inactive_offer_variants(updated)
            updated = replace_data_copy(updated, "data-offer-copy", offer_copy, state=state)
        if updated != html:
            desired[path] = updated
    return state, desired


def main():
    args = parse_args()
    now = parsed_time(args.at)
    state, desired = desired_files(now)
    changed = [path for path, value in desired.items() if path.read_text(encoding="utf-8") != value]
    if args.check:
        if changed:
            print(f"content drift ({state} offer):")
            for path in changed:
                print(path.relative_to(ROOT))
            return 1
        print(f"content sync check passed ({state} offer)")
        return 0

    for path in changed:
        path.write_text(desired[path], encoding="utf-8")
    print(f"synced {len(changed)} files ({state} offer)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
