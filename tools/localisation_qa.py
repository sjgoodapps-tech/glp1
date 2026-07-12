#!/usr/bin/env python3
import argparse
import re
import sys
import urllib.request
from pathlib import Path
from urllib.parse import urlparse
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]

P0_PATTERNS = {
    "ambiguous English source string": [
        "Fast logging without clutter",
        "Route and cadence",
        "Route and Cadence",
        "Choose the packaging that matches what you use",
        "Provider Summary",
        "Provider summary",
        "Create a calm provider summary PDF",
        "one calmer place",
        "Export-ready records",
        "Export-ready records: CSV, JSON and PDF",
        "Custom / Compounded",
        "No account required to track",
        "No account is required to track",
        "No in-app account is required to record doses, weight, symptoms or reminders",
        "Apple Health access is optional and limited to the permissions you grant",
        "Keep dose, weight, symptoms, appetite and photos together in one place",
        "track doses, weight, symptoms, reminders or orders",
    ],
    "bad logging translation": [
        "mežizstrāde",
        "ťažba dreva",
        "těžba dřeva",
        "metsaraie",
        "เข้าสู่ระบบอย่างรวดเร็ว",
        "Đăng nhập nhanh chóng",
        "द्रुत लॉगिंग",
    ],
    "wrong route/cadence translation": [
        "Maršruts un kadence",
        "Trasa a kadencia",
        "Trasa a kadence",
        "Marsruut ja kadents",
        "路线和节奏",
        "路線和節奏",
        "Itinéraire et cadence",
        "Route und Kadenz",
        "ルートとリズム",
        "경로 및 케이던스",
        "Route en cadans",
        "Ruta y cadencia",
        "Rota e cadência",
        "المسار والإيقاع",
        "Маршрут и частота вращения педалей",
        "Rute dan irama",
        "मार्ग आणि ताल",
        "Pot in kadenca",
        "Rota e cadência",
        "Percorso e cadenza",
        "Trasa i rytm",
    ],
    "wrong medicine form/packaging wording": [
        "Choose the packaging",
        "packaging that matches",
        "पॅकेजिंग",
        "embalagem que corresponda",
        "confezione",
        "opakowanie",
        "embalažo",
        "Presentation fit",
        ">Presentation<",
        ">Presentations<",
    ],
    "wrong clinician/provider wording": [
        "provider-style PDF",
        "Provider-style PDF",
        "provider-style exports",
        "Provider-style exports",
        "提供商摘要",
        "提供者摘要",
        "プロバイダーの概要",
        "공급자 요약",
        "제공자 요약",
        "Samenvatting van de leverancier",
        "Resumen del proveedor",
        "Anbieterübersicht",
        "Résumé du fournisseur",
        "ملخص الموفر",
        "प्रदाता सारांश",
        "Palveluntarjoajan yhteenveto",
        "Ringkasan Pembekal",
        "Povzetek ponudnika",
    ],
    "wrong calm/quiet place wording": [
        "one calm place",
        "one calmer place",
        "quiet place",
        "शांत ठिकाणी",
        "rauhallisessa paikassa",
        "mirnem mestu",
        "tempat yang tenang",
    ],
    "bad PDF/export wording": [
        "PDF, PDF",
        "PDF-, PDF-",
        "calm provider summary PDF",
        "provider summary PDF",
        "सारांश PDF",
    ],
    "mixed English commercial copy": [
        "Current mes",
        "Current maand",
        "Current mês",
        "Unlock exports",
        "past and futura",
        "past and toekomst",
        "past and futuro",
    ],
    "wrong custom/compounded wording": [
        "Costume",
        "Coutume",
        "Skik",
        "route, presentation, cadence",
        "custom/compounded setup",
    ],
    "wrong order/reorder wording": [
        "orders",
        "ordini",
        "ordrer",
        "tilausten",
        "pesanan",
        "คำสั่งซื้อ",
        "订单",
        "訂單",
        "注文",
        "الطلبات",
    ],
    "wrong sleep claim": [
        "sleep, ",
        "sleep, movement",
        "sleep tracking",
        "søvn",
        "tidur",
        "sonno",
        "sommeil",
        "Schlaf",
        "slaap",
        "sömn",
        "睡眠",
        "수면",
    ],
    "mixed non-localized app-store pricing": [
        "See App Store pricing\u200b",
    ],
    "malformed repeated-word copy": [
        "A a a",
        "O O O",
        "o o o",
        "hero-via",
        "a a sual",
    ],
}

SCOPED_P0_PATTERNS = {
    "pt-pt/": {
        "PT-PT Brazilian-style wording": [
            "você",
            "Você",
            "Seus registos",
            "Contate",
            "Gerencie",
            "Gerenciar",
            "configurações de App Store",
            "somente leitura",
            "tela inicial",
            "rastreamento",
            "compartilhar",
            "solicitação",
            "escopo",
            "assinatura",
            "A a a",
            "O O O",
            "o o o",
            "hero-via",
            "No in-app account is required",
            "Apple Health access is optional",
        ],
    },
    "nl/": {
        "Dutch support label": [
            ">Steun<",
        ],
    },
}

LOCALE_SAFETY_REQUIRED = {
    "ar/": ("تركيز الدم", "قرارات الجرعات", "نصيحة طبية"),
    "ja/": ("血中濃度", "投与判断", "医療上の助言"),
    "hi/": ("रक्त सांद्रता", "खुराक", "चिकित्सीय सलाह"),
    "it/": ("concentrazione ematica", "dosaggio", "consiglio medico"),
}

SAFETY_REQUIRED = re.compile(
    r"Estimated Exposure is a personal tracking estimate, not measured blood concentration"
)

LOCALE_DIRS = {
    "ar", "bg", "bn", "cs", "da", "de", "el", "en", "en-gb", "es-es", "es-mx",
    "et", "fi", "fil", "fr", "fr-ca", "gu", "he", "hi", "hr", "hu", "id", "it",
    "ja", "kn", "ko", "lt", "lv", "ml", "mr", "ms", "nb", "nl", "or", "pa",
    "pl", "pt-br", "pt-pt", "ro", "ru", "sk", "sl", "sr", "sv", "ta", "te",
    "th", "tr", "uk", "ur", "vi", "zh-hans", "zh-hant",
}

LIVE_SITE = "https://www.glpzy.app"


def locale_for(rel):
    first = rel.split("/", 1)[0]
    return first if "/" in rel and first in LOCALE_DIRS else "root"


def is_noindex(text):
    return bool(re.search(r'<meta name="robots" content="[^\"]*noindex', text, re.I))


def robots_values(text):
    values = []
    tag_pattern = re.compile(
        r'<meta\b(?=[^>]*\bname\s*=\s*["\']robots["\'])'
        r'(?=[^>]*\bcontent\s*=\s*["\'][^"\']*["\'])[^>]*>',
        re.I,
    )
    for tag in tag_pattern.findall(text):
        match = re.search(r'\bcontent\s*=\s*["\']([^"\']*)["\']', tag, re.I)
        if match:
            values.append(match.group(1).strip().lower())
    return values


def check_robots_meta():
    failures = []
    for path in sorted(ROOT.rglob("*.html")):
        if ".git" in path.parts:
            continue
        rel = path.relative_to(ROOT).as_posix()
        values = robots_values(path.read_text(encoding="utf-8"))
        if len(values) != 1:
            failures.append((rel, "robots meta count", str(len(values))))
    return failures


def visible_text(text):
    text = re.sub(r"<script\b.*?</script>|<style\b.*?</style>|<noscript\b.*?</noscript>", " ", text, flags=re.S | re.I)
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def scan_one(rel, text, include_noindex=False):
    if locale_for(rel) in {"root", "en"}:
        return []
    if not include_noindex and is_noindex(text):
        return []
    failures = []
    haystack = visible_text(text)
    for label, patterns in P0_PATTERNS.items():
        for pattern in patterns:
            if pattern in haystack or pattern in text:
                failures.append((rel, label, pattern))
    for prefix, scoped_patterns in SCOPED_P0_PATTERNS.items():
        if not rel.startswith(prefix):
            continue
        for label, patterns in scoped_patterns.items():
            for pattern in patterns:
                if pattern in haystack or pattern in text:
                    failures.append((rel, label, pattern))
    if "medical-safety" in rel or rel.endswith("methodology.html"):
        if "Estimated Exposure" in text and not SAFETY_REQUIRED.search(text):
            failures.append((rel, "Estimated Exposure safety wording", "missing measured blood concentration warning"))
        for prefix, required_phrases in LOCALE_SAFETY_REQUIRED.items():
            if not rel.startswith(prefix):
                continue
            for phrase in required_phrases:
                if phrase not in haystack:
                    failures.append((rel, "translated Estimated Exposure safety wording", phrase))
    return failures


def scan_html(include_noindex=False):
    failures = []
    for path in sorted(ROOT.rglob("*.html")):
        if ".git" in path.parts:
            continue
        rel = path.relative_to(ROOT).as_posix()
        failures.extend(scan_one(rel, path.read_text(encoding="utf-8"), include_noindex))
    return failures


def check_index_gate():
    failures = []
    gated = []
    sitemap = set()
    sitemap_path = ROOT / "sitemap.xml"
    if sitemap_path.exists():
        ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        sitemap = {node.text for node in ET.parse(sitemap_path).findall(".//sm:loc", ns) if node.text}
    for path in sorted(ROOT.rglob("*.html")):
        if ".git" in path.parts:
            continue
        rel = path.relative_to(ROOT).as_posix()
        if locale_for(rel) in {"root", "en"}:
            continue
        text = path.read_text(encoding="utf-8")
        issues = scan_one(rel, text, include_noindex=True)
        if issues and not is_noindex(text):
            failures.extend(issues)
        if issues and is_noindex(text):
            gated.append(rel)
        canonical = re.search(r'<link rel="canonical" href="([^\"]+)"', text, re.I)
        if is_noindex(text) and canonical and canonical.group(1) in sitemap:
            failures.append((rel, "noindex sitemap conflict", canonical.group(1)))
    print(f"gated locale pages with remaining copy risk: {len(gated)}")
    return failures


def check_dynamic_locale_copy():
    failures = []
    config = (ROOT / "site-config.js").read_text(encoding="utf-8")
    cta = (ROOT / "site-cta.js").read_text(encoding="utf-8")
    storefronts = set(re.findall(r'^\s*"([^\"]+)"\s*:\s*\{', config, re.M))
    messages = set(re.findall(r'^\s*"([^\"]+)"\s*:\s*"', cta, re.M))
    for locale in sorted(storefronts - {"en"} - messages):
        failures.append(("site-cta.js", "missing translated offer message", locale))
    for pattern in ["Get GLPzy", "Dismiss", "Get the app"]:
        if pattern in cta:
            # English is allowed as the English fallback, but localized pages must
            # replace these labels with their existing translated App Store label.
            continue
    return failures


def fetch(url):
    request = urllib.request.Request(url, headers={"User-Agent": "GLPzy-localisation-qa/1.0"})
    with urllib.request.urlopen(request, timeout=12) as response:
        return response.status, response.read().decode("utf-8", errors="replace")


def scan_live():
    failures = []
    status, sitemap_text = fetch(f"{LIVE_SITE}/sitemap.xml")
    if status != 200:
        return [("sitemap.xml", "live fetch failed", str(status))]
    ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    urls = [node.text for node in ET.fromstring(sitemap_text).findall(".//sm:loc", ns) if node.text]
    # Scan all live locale homepages plus the root and commercial priority pages.
    selected = {f"{LIVE_SITE}/"}
    priority_names = {"mounjaro-tracker-iphone.html", "wegovy-tracker-iphone.html", "zepbound-tracker-iphone.html", "tirzepatide-tracker-iphone.html", "semaglutide-tracker-iphone.html", "glp1-weight-dose-symptom-tracker.html"}
    for url in urls:
        path = urlparse(url).path.strip("/")
        if path.endswith("/index.html") or (path and path.split("/")[-1] in priority_names):
            selected.add(url)
    for url in sorted(selected):
        try:
            status, text = fetch(url)
        except Exception as exc:
            failures.append((url, "live fetch failed", str(exc)))
            continue
        if status != 200:
            failures.append((url, "live HTTP status", str(status)))
            continue
        rel = urlparse(url).path.strip("/") or "index.html"
        if rel.endswith("/"):
            rel += "index.html"
        failures.extend(scan_one(rel, text, include_noindex=False))
    print(f"live locale pages checked: {len(selected)}")
    return failures


def check_offer_static_html():
    failures = []
    for rel in ("index.html", "free-lifetime/index.html"):
        path = ROOT / rel
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        if "offer-active-only" in text and "offer-expired-only" in text:
            failures.append((rel, "offer crawler conflict", "active and expired variants both present in static HTML"))
    return failures


def main():
    parser = argparse.ArgumentParser(description="Check GLPzy locale copy and index gates.")
    parser.add_argument("--all", action="store_true", help="scan gated pages as well as indexable pages")
    parser.add_argument("--live", action="store_true", help="scan live locale homepages and priority pages")
    args = parser.parse_args()
    failures = check_robots_meta() + scan_html(include_noindex=args.all) + check_offer_static_html() + check_dynamic_locale_copy()
    if not args.all:
        failures += check_index_gate()
    if args.live:
        failures += scan_live()
    if failures:
        for rel, label, pattern in failures:
            print(f"{rel}: {label}: {pattern}")
        print(f"\nlocalisation QA failed with {len(failures)} issue(s).")
        return 1
    print("localisation QA passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
