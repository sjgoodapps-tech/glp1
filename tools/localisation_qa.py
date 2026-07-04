#!/usr/bin/env python3
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

P0_PATTERNS = {
    "bad logging translation": [
        "mežizstrāde",
        "ťažba dreva",
        "těžba dřeva",
        "metsaraie",
        "เข้าสู่ระบบอย่างรวดเร็ว",
        "Đăng nhập nhanh chóng",
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
    ],
    "wrong clinician/provider wording": [
        "provider-style PDF",
        "Provider-style PDF",
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
    ],
    "bad PDF/export wording": [
        "PDF, PDF",
        "PDF-, PDF-",
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
        "คำสั่งซื้อ",
        "订单",
        "訂單",
        "注文",
        "الطلبات",
    ],
    "wrong sleep claim": [
        "sleep, movement",
        "sleep tracking",
    ],
    "mixed non-localized app-store pricing": [
        "See App Store pricing\u200b",
    ],
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
