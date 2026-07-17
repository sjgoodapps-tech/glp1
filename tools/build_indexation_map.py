#!/usr/bin/env python3
import csv
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INVENTORY = ROOT / "reports" / "seo-url-inventory.csv"
MAP_CSV = ROOT / "reports" / "indexation-consolidation-map.csv"
MAP_MD = ROOT / "reports" / "indexation-consolidation-summary.md"
LOCALE_POLICY = json.loads((ROOT / "data" / "locale-indexing.json").read_text(encoding="utf-8"))
REVIEWED_LOCALES = {item.lower() for item in LOCALE_POLICY["native_reviewed_locales"]}

PRIORITY_PATHS = {
    "index.html",
    "free-lifetime/index.html",
    "glp1-weight-dose-symptom-tracker.html",
    "mounjaro-tracker-iphone.html",
    "wegovy-tracker-iphone.html",
    "zepbound-tracker-iphone.html",
    "tirzepatide-tracker-iphone.html",
    "semaglutide-tracker-iphone.html",
    "local-first-private-glp-tracker.html",
    "glp1-dose-reminder-app.html",
    "glp1-side-effect-symptom-tracker.html",
    "glp1-weight-tracker.html",
    "glp1-progress-photo-tracker.html",
    "apple-health-glp-tracker.html",
    "privacy.html",
    "medical-safety.html",
    "methodology.html",
    "support.html",
    "data-rights.html",
}

CONSOLIDATION_TARGETS = {
    "ozempic-tracker-iphone.html": "semaglutide-tracker-iphone.html",
    "rybelsus-tracker-iphone.html": "semaglutide-tracker-iphone.html",
    "saxenda-tracker-iphone.html": "glp1-weight-dose-symptom-tracker.html",
    "victoza-tracker-iphone.html": "glp1-weight-dose-symptom-tracker.html",
    "trulicity-tracker-iphone.html": "glp1-weight-dose-symptom-tracker.html",
    "foundayo-tracker-iphone.html": "glp1-weight-dose-symptom-tracker.html",
    "custom-medication-tracker-iphone.html": "glp1-weight-dose-symptom-tracker.html",
    "compounded-glp-tracker-iphone.html": "glp1-weight-dose-symptom-tracker.html",
}


def decision(row):
    path = row["path"]
    locale = row["locale"].lower()
    indexed = row["index_noindex"] == "index"

    if locale == "root":
        if path in PRIORITY_PATHS:
            return (
                "keep_index_priority",
                "",
                "P0",
                "Distinct product, feature, offer or trust intent.",
                "Monitor query match, CTR, canonical selection and conversions.",
            )
        if not indexed:
            return (
                "review_root_noindex",
                row["canonical_url"],
                "P1",
                "Root English page is currently noindex and needs an explicit decision.",
                "Confirm whether the page has a unique user and search purpose.",
            )
        target = CONSOLIDATION_TARGETS.get(Path(path).name, "")
        if target:
            return (
                "monitor_then_consolidate",
                f"https://www.glpzy.app/{target}",
                "P1",
                "The page overlaps a broader ingredient or tracker intent.",
                "Keep for 28 days, then merge only if Search Console shows no distinct query demand.",
            )
        return (
            "keep_index_supporting",
            "",
            "P2",
            "Indexable root page with a supporting policy or product role.",
            "Monitor impressions, internal links and canonical selection.",
        )

    if locale == "en":
        return (
            "keep_noindex_duplicate",
            row["canonical_url"],
            "P0",
            "The /en/ page duplicates the root English page.",
            "Confirm Google drops the duplicate after recrawl.",
        )

    if locale not in REVIEWED_LOCALES:
        return (
            "keep_noindex_pending_native_review",
            "",
            "P0",
            "No documented native-language approval exists for this locale.",
            "Native copy, medical wording and mobile layout must pass before indexing.",
        )

    return (
        "keep_index_native_reviewed" if indexed else "review_native_locale_gate",
        "",
        "P1",
        "Locale is recorded as native-reviewed.",
        "Confirm hreflang reciprocity, canonical URL and Search Console coverage.",
    )


def main():
    with INVENTORY.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))

    output = []
    counts = Counter()
    for row in rows:
        action, target, priority, reason, evidence = decision(row)
        counts[action] += 1
        output.append(
            {
                "url": row["url"],
                "path": row["path"],
                "locale": row["locale"],
                "page_family": row["page_family"],
                "current_index_state": row["index_noindex"],
                "in_sitemap": row["sitemap_included"],
                "canonical_url": row["canonical_url"],
                "recommended_action": action,
                "consolidation_target": target,
                "priority": priority,
                "reason": reason,
                "evidence_required": evidence,
            }
        )

    fields = list(output[0])
    with MAP_CSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(output)

    lines = [
        "# Indexation and Consolidation Summary",
        "",
        f"Generated: {datetime.now(timezone.utc).isoformat(timespec='seconds')}",
        f"Pages mapped: {len(output)}",
        f"Native-reviewed locales: {', '.join(sorted(REVIEWED_LOCALES)) or 'none'}",
        "",
        "## Decision Counts",
        "",
    ]
    for action, count in sorted(counts.items()):
        lines.append(f"- `{action}`: {count}")
    lines.extend(
        [
            "",
            "## Rules",
            "",
            "- Root English priority and trust pages remain indexable.",
            "- `/en/` duplicates remain `noindex,follow` and point to root English canonicals.",
            "- A locale is not indexable until native approval is recorded in `data/locale-indexing.json`.",
            "- Overlapping root medicine pages are not merged without at least 28 days of Search Console query data.",
            "- A consolidation target is a decision aid, not an automatic redirect instruction.",
        ]
    )
    MAP_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {MAP_CSV.relative_to(ROOT)} with {len(output)} pages")
    print(f"wrote {MAP_MD.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
