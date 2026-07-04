#!/usr/bin/env python3
import re
import sys
from pathlib import Path

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
        ],
    },
    "nl/": {
        "Dutch support label": [
            ">Steun<",
        ],
    },
}

SAFETY_REQUIRED = re.compile(
    r"Estimated Exposure is a personal tracking estimate, not measured blood concentration"
)


def scan_html():
    failures = []
    for path in sorted(ROOT.rglob("*.html")):
        if ".git" in path.parts:
            continue
        text = path.read_text(encoding="utf-8")
        rel = path.relative_to(ROOT).as_posix()
        for label, patterns in P0_PATTERNS.items():
            for pattern in patterns:
                if pattern in text:
                    failures.append((rel, label, pattern))
        for prefix, scoped_patterns in SCOPED_P0_PATTERNS.items():
            if not rel.startswith(prefix):
                continue
            for label, patterns in scoped_patterns.items():
                for pattern in patterns:
                    if pattern in text:
                        failures.append((rel, label, pattern))
        if "medical-safety" in rel or rel.endswith("methodology.html"):
            if "Estimated Exposure" in text and not SAFETY_REQUIRED.search(text):
                failures.append((rel, "Estimated Exposure safety wording", "missing measured blood concentration warning"))
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
    failures = scan_html() + check_offer_static_html()
    if failures:
        for rel, label, pattern in failures:
            print(f"{rel}: {label}: {pattern}")
        print(f"\nlocalisation QA failed with {len(failures)} issue(s).")
        return 1
    print("localisation QA passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
