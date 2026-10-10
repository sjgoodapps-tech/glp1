#!/usr/bin/env python3
"""Audit English-content parity without altering site files.

This is a structural *necessary* check, not a machine-translation or native-language
quality certification. Use --gate only when the target locales have been completed.
"""
from __future__ import annotations

import argparse
import json
import re
from html import unescape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PRIORITY = (
    "es-es", "es-mx", "de", "fr", "fr-ca", "pt-br", "pt-pt",
    "ar", "zh-hans", "zh-hant", "ja", "ko", "hi", "it",
)
ESSENTIAL = (
    "privacy.html", "data-rights.html", "terms.html",
    "medical-safety.html", "methodology.html", "support.html",
)
# True English-only pages must be inventoried as gaps, not silently ignored.
EXPECTED_EXCEPTIONS = {"languages.html", "free-lifetime/index.html"}
TAG_TEMPLATE = r"<{tag}\b[^>]*>"
HTML_LANG = re.compile(r"<html\b[^>]*\blang=['\"]([^'\"]+)", re.I)
HTML_DIR = re.compile(r"<html\b[^>]*\bdir=['\"]([^'\"]+)", re.I)
MAIN = re.compile(r"<main\b[^>]*>[\s\S]*?</main>", re.I)
NUM_HEADING = re.compile(r"<h2\b[^>]*>\s*(\d+)\.\s*[\s\S]*?</h2>", re.I)
ALLOWED_LATIN = re.compile(r"OneGLP|GLPzy|GLP-1|Apple Health|App Store")


def tag_count(markup: str, tag: str) -> int:
    return len(re.findall(TAG_TEMPLATE.format(tag=re.escape(tag)), markup, re.I))


def main_markup(html: str) -> str:
    match = MAIN.search(html)
    return match.group(0) if match else ""


def facts(html: str) -> dict:
    body = main_markup(html)
    clean = unescape(re.sub(r"<[^>]+>", " ", body))
    return {
        "has_main": bool(body),
        "sections": tag_count(body, "section"),
        "h2": tag_count(body, "h2"),
        "h3": tag_count(body, "h3"),
        "paragraphs": tag_count(body, "p"),
        "list_items": tag_count(body, "li"),
        "table_rows": tag_count(body, "tr"),
        "numbered_headings": [int(n) for n in NUM_HEADING.findall(body)],
        "text_characters": len(re.sub(r"\s+", " ", clean).strip()),
    }


def audits(root: Path, targets: tuple[str, ...] = PRIORITY) -> dict:
    if any("/" in l or ".." in l for l in targets):
        raise ValueError("Invalid locale path")
    english_pages = {
        p.relative_to(root).as_posix(): p
        for p in root.rglob("*.html")
        if len(p.relative_to(root).parts) == 1 or
           p.relative_to(root).parts[0] in {"free-lifetime", "press", "glpzy-is-now-oneglp"}
    }
    # Root equivalents, including subdirectories, are the English reference.
    english_pages = {p: path for p, path in english_pages.items()
                     if not p.startswith("en/")}
    reference = {p: facts(path.read_text(encoding="utf-8"))
                 for p, path in english_pages.items()}
    review = json.loads((root / "data" / "locale-indexing.json").read_text(encoding="utf-8"))
    native_approved = set(review.get("native_reviewed_locales", []))
    result = {"baseline": "root English", "priority_locales": list(targets),
              "native_approved": sorted(native_approved & set(targets)),
              "source_review_history": [
                  "2026-10-10: English terms/support reconciled with non-renewing founding Lifetime Premium entitlement and oneglp.app canonical host.",
                  "2026-10-10: medical-safety Trulicity daily/weekly grouping corrected against labelled weekly administration."
              ], "locales": {}}
    for locale in targets:
        records, missing, errors = [], [], []
        for page in sorted(english_pages):
            p = root / locale / page
            if not p.is_file():
                if page not in EXPECTED_EXCEPTIONS:
                    missing.append(page)
                continue
            local = p.read_text(encoding="utf-8")
            baseline = reference[page]
            current = facts(local)
            defects = []
            if page in ESSENTIAL:
                # Counting is an indicator, not proof of semantic equivalence.
                for field in ("sections", "paragraphs", "list_items", "table_rows"):
                    if current[field] < baseline[field]:
                        defects.append(f"{field}: {current[field]} vs English {baseline[field]}")
                req = set(baseline["numbered_headings"])
                got = set(current["numbered_headings"])
                if req and got != req:
                    defects.append(f"numbered policy sections: {len(got)} vs English {len(req)}")
            if not current["has_main"]:
                defects.append("missing <main> element")
            lang = HTML_LANG.search(local)
            if not lang or lang.group(1).replace("_", "-").lower() != locale:
                defects.append("HTML lang mismatches locale")
            is_rtl = locale in {"ar", "he", "ur"}
            direction = HTML_DIR.search(local)
            if is_rtl and (not direction or direction.group(1).lower() != "rtl"):
                defects.append("missing right-to-left document direction")
            if re.search(r'<meta\b(?=[^>]*name=["\']robots["\'])[^>]*noindex', local, re.I):
                defects.append("noindex disallowed for published translation")
            if defects:
                errors.append({"page": page, "issues": defects})
            if page in ESSENTIAL:
                records.append({"page": page, "english": baseline,
                                "localised": current, "issues": defects})
        result["locales"][locale] = {
            "pages_present": len(english_pages) - len(missing),
            "english_pages": len(english_pages),
            "missing_pages": missing,
            "essential": records,
            "essential_errors": [x for x in errors if x["page"] in ESSENTIAL] + [
                {"page": x, "issues": ["essential page missing"]}
                for x in ESSENTIAL if x in missing
            ],
            "structural_errors": errors,
            "structural_gate": "PASS" if not errors and not missing else "FAIL",
            "native_review": "approved" if locale in native_approved else "pending",
            "semantic_translation_review": "not certified by this script",
            "mobile_visual_review": "not certified by this script",
        }
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--locale", action="append", choices=PRIORITY,
                        help="Repeat to check selected locales (default: all 14)")
    parser.add_argument("--gate", action="store_true",
                        help="Exit nonzero if any locale is structurally incomplete")
    parser.add_argument("--gate-essential", action="store_true",
                        help="Exit nonzero only for essential-document coverage errors")
    parser.add_argument("--output", type=Path, help="Optional output JSON report")
    args = parser.parse_args()
    report = audits(ROOT, tuple(args.locale) if args.locale else PRIORITY)
    payload = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8")
    totals = [(l, len(v["missing_pages"]), len(v["structural_errors"]))
              for l, v in report["locales"].items()]
    print("OneGLP priority locale structural audit (not translation approval)")
    for loc, missing, errors in totals:
        print(f"  {loc:8} missing pages={missing:2} pages with issues={errors:2}")
    print("Source reconciliation notes:", len(report["source_review_history"]))
    if args.output:
        print("JSON report:", args.output)
    structural_fail = args.gate and any(missing or errors for _, missing, errors in totals)
    essential_fail = args.gate_essential and any(
        record["essential_errors"] for record in report["locales"].values()
    )
    return int(structural_fail or essential_fail)


if __name__ == "__main__":
    raise SystemExit(main())
