#!/usr/bin/env python3
import argparse
import json
import os
import shutil
import statistics
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
REPORT_JSON = ROOT / "reports" / "lighthouse-baseline.json"
REPORT_MD = ROOT / "reports" / "lighthouse-baseline.md"

PAGES = [
    ("homepage", ""),
    ("glp1-tracker", "glp1-weight-dose-symptom-tracker.html"),
    ("mounjaro", "mounjaro-tracker-iphone.html"),
    ("wegovy", "wegovy-tracker-iphone.html"),
    ("zepbound", "zepbound-tracker-iphone.html"),
    ("tirzepatide", "tirzepatide-tracker-iphone.html"),
    ("semaglutide", "semaglutide-tracker-iphone.html"),
    ("privacy", "local-first-private-glp-tracker.html"),
    ("dose-reminder", "glp1-dose-reminder-app.html"),
    ("symptoms", "glp1-side-effect-symptom-tracker.html"),
    ("weight", "glp1-weight-tracker.html"),
    ("photos", "glp1-progress-photo-tracker.html"),
    ("apple-health", "apple-health-glp-tracker.html"),
]

AUDITS = {
    "first-contentful-paint": "fcp_ms",
    "largest-contentful-paint": "lcp_ms",
    "total-blocking-time": "tbt_ms",
    "cumulative-layout-shift": "cls",
    "speed-index": "speed_index_ms",
    "total-byte-weight": "total_bytes",
}


def default_node():
    found = shutil.which("node")
    if found:
        return found
    bundled = Path.home() / ".cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node"
    return str(bundled)


def default_chrome():
    matches = sorted(
        (Path.home() / "Library/Caches/ms-playwright").glob(
            "chromium-*/chrome-mac-arm64/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing"
        )
    )
    return str(matches[-1]) if matches else ""


def parse_args():
    parser = argparse.ArgumentParser(description="Run a local Lighthouse baseline for GLPzy priority pages.")
    parser.add_argument("--base-url", default="http://127.0.0.1:4173/")
    parser.add_argument("--node", default=default_node())
    parser.add_argument("--chrome-path", default=default_chrome())
    parser.add_argument("--lighthouse-cli", default="/tmp/glpzy-lighthouse/node_modules/lighthouse/cli/index.js")
    parser.add_argument("--output-dir", default="/tmp/glpzy-lighthouse-results")
    parser.add_argument("--mobile-only", action="store_true")
    parser.add_argument(
        "--runs",
        type=int,
        default=3,
        help="Runs per page and mode. The report uses the median to reduce synthetic variance.",
    )
    return parser.parse_args()


def score(category):
    value = category.get("score")
    return round(value * 100) if isinstance(value, (int, float)) else None


def run_one(args, name, page, strategy, output_dir, run_number):
    url = args.base_url.rstrip("/") + "/" + page
    output = output_dir / f"{name}-{strategy}-run{run_number}.json"
    command = [
        args.node,
        args.lighthouse_cli,
        url,
        "--quiet",
        "--output=json",
        f"--output-path={output}",
        "--only-categories=performance,accessibility,best-practices,seo",
        "--throttling-method=simulate",
        "--chrome-flags=--headless=new --no-sandbox --disable-gpu",
    ]
    if strategy == "desktop":
        command.append("--preset=desktop")
    environment = os.environ.copy()
    environment["CHROME_PATH"] = args.chrome_path
    process = subprocess.run(
        command,
        cwd=ROOT,
        env=environment,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    if process.returncode != 0:
        raise RuntimeError(f"Lighthouse failed for {name} {strategy}: {process.stdout[-2000:]}")
    data = json.loads(output.read_text(encoding="utf-8"))
    categories = data["categories"]
    record = {
        "page": name,
        "path": page or "index.html",
        "strategy": strategy,
        "performance": score(categories["performance"]),
        "accessibility": score(categories["accessibility"]),
        "best_practices": score(categories["best-practices"]),
        "seo": score(categories["seo"]),
    }
    for audit_id, field in AUDITS.items():
        value = data.get("audits", {}).get(audit_id, {}).get("numericValue")
        record[field] = round(value, 3) if isinstance(value, (int, float)) else None
    return record, data.get("lighthouseVersion", "unknown")


def median_record(samples):
    result = {
        "page": samples[0]["page"],
        "path": samples[0]["path"],
        "strategy": samples[0]["strategy"],
        "sample_count": len(samples),
    }
    integer_fields = ["performance", "accessibility", "best_practices", "seo"]
    metric_fields = list(AUDITS.values())
    for field in integer_fields:
        result[field] = round(statistics.median(item[field] for item in samples))
    for field in metric_fields:
        values = [item[field] for item in samples if item[field] is not None]
        result[field] = round(statistics.median(values), 3) if values else None
    result["sample_lcp_ms"] = [item["lcp_ms"] for item in samples]
    result["sample_cls"] = [item["cls"] for item in samples]
    result["sample_performance"] = [item["performance"] for item in samples]
    return result


def threshold_result(record):
    checks = {
        "performance": record["performance"] >= 90,
        "accessibility": record["accessibility"] >= 95,
        "best_practices": record["best_practices"] >= 95,
        "seo": record["seo"] >= 95,
        "lcp": record["lcp_ms"] is not None and record["lcp_ms"] <= 2500,
        "cls": record["cls"] is not None and record["cls"] <= 0.1,
        "tbt": record["tbt_ms"] is not None and record["tbt_ms"] <= 200,
    }
    return all(checks.values()), [name for name, ok in checks.items() if not ok]


def write_reports(records, version, base_url, runs):
    for record in records:
        passed, failures = threshold_result(record)
        record["release_threshold_pass"] = passed
        record["threshold_failures"] = failures
    payload = {
        "generated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "lighthouse_version": version,
        "base_url": base_url,
        "run_type": f"{runs}-run median local live-equivalent synthetic baseline",
        "runs_per_page_and_mode": runs,
        "thresholds": {
            "performance": 90,
            "accessibility": 95,
            "best_practices": 95,
            "seo": 95,
            "lcp_ms_max": 2500,
            "cls_max": 0.1,
            "tbt_ms_max": 200,
        },
        "results": records,
    }
    REPORT_JSON.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# Lighthouse Baseline",
        "",
        f"Generated: {payload['generated']}",
        f"Lighthouse: {version}",
        f"Run type: {runs}-run median local live-equivalent synthetic baseline",
        "",
        "Each row is the median of repeated synthetic runs. These results are useful for regression checks, but they are not field Core Web Vitals or Chrome UX Report data.",
        "",
        "| Page | Mode | Perf | A11y | Best | SEO | LCP ms | CLS | TBT ms | Bytes | Gate |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for item in records:
        gate = "Pass" if item["release_threshold_pass"] else "Review: " + ", ".join(item["threshold_failures"])
        lines.append(
            f"| {item['page']} | {item['strategy']} | {item['performance']} | {item['accessibility']} | "
            f"{item['best_practices']} | {item['seo']} | {round(item['lcp_ms'])} | {item['cls']:.3f} | "
            f"{round(item['tbt_ms'])} | {round(item['total_bytes'])} | {gate} |"
        )
    lines.extend(
        [
            "",
            "## Release Threshold",
            "",
            "Performance 90, accessibility 95, best practices 95, SEO 95, LCP no more than 2.5 seconds, CLS no more than 0.1 and TBT no more than 200 ms.",
            "",
            "## Limits",
            "",
            "- Validate the deployed site again after release.",
            "- Use Search Console Core Web Vitals and CrUX data when enough real traffic is available.",
            "- Compare future runs with the same Lighthouse version, browser and throttling settings.",
        ]
    )
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    args = parse_args()
    if args.runs < 1:
        print("--runs must be at least 1")
        return 2
    for required in [args.node, args.chrome_path, args.lighthouse_cli]:
        if not required or not Path(required).exists():
            print(f"Missing Lighthouse dependency: {required or '(not configured)'}")
            return 2
    try:
        with urlopen(args.base_url, timeout=5) as response:
            if response.status != 200:
                raise RuntimeError(f"Local server returned {response.status}")
    except Exception as exc:
        print(f"Cannot reach local server at {args.base_url}: {exc}")
        return 2

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    strategies = ["mobile"] if args.mobile_only else ["mobile", "desktop"]
    records = []
    version = "unknown"
    for strategy in strategies:
        for name, page in PAGES:
            samples = []
            for run_number in range(1, args.runs + 1):
                print(f"Lighthouse {strategy}: {name} ({run_number}/{args.runs})", flush=True)
                record, version = run_one(args, name, page, strategy, output_dir, run_number)
                samples.append(record)
            records.append(median_record(samples))
    write_reports(records, version, args.base_url, args.runs)
    failed = sum(not threshold_result(item)[0] for item in records)
    print(f"wrote {REPORT_JSON.relative_to(ROOT)}")
    print(f"wrote {REPORT_MD.relative_to(ROOT)}")
    print(f"completed {len(records)} audits; {failed} require review")
    return 0


if __name__ == "__main__":
    sys.exit(main())
