#!/usr/bin/env python3
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REPLACEMENTS = {
    # English source and generated English pages.
    "daily logging": "daily dose entry",
    "Fast dose logging": "Fast dose entry",
    "provider-style PDF summaries": "clinician-ready PDF summaries",
    "Provider-style PDF summaries": "Clinician-ready PDF summaries",
    "Supply logging": "Supply tracking",
    "route, presentation, cadence, or custom/compounded setup": "administration route, medicine form, dosing frequency, custom treatment, or compounded treatment setup",
    "Estimated medication level for personal tracking only. Not medical advice. Always check with your clinician before making medical decisions.": "Estimated Exposure is a personal tracking estimate, not measured blood concentration and not medical advice. Do not use Estimated Exposure to guide dosing. Always check with your clinician before making medical decisions.",
    "Estimated medication level for personal tracking only. Not medical advice.": "Estimated Exposure is a personal tracking estimate, not measured blood concentration and not medical advice.",
    "Always check with your clinician before making medical decisions.": "Do not use Estimated Exposure to guide dosing. Always check with your clinician before making medical decisions.",
    "sleep, ": "",
    "sleep, movement": "movement",

    # Repeated CSV/PDF and mixed-English fragments.
    "PDF, PDF and PDF summaries": "CSV, JSON and PDF summaries",
    "PDF-, PDF- en PDF-samenvattingen": "CSV-, JSON- en PDF-samenvattingen",
    "PDF-, PDF- und PDF-Zusammenfassungen": "CSV-, JSON- und PDF-Zusammenfassungen",
    "PDF, PDF og PDF": "CSV, JSON og PDF",
    "PDF, PDF och PDF": "CSV, JSON och PDF",
    "PDF, PDF ja PDF": "CSV, JSON ja PDF",
    "PDF, PDF 및 PDF": "CSV, JSON 및 PDF",
    "PDF, PDF y PDF": "CSV, JSON y PDF",
    "PDF, PDF e PDF": "CSV, JSON e PDF",
    "PDF, PDF et PDF": "CSV, JSON et PDF",
    "Podsumowania PDF, PDF i PDF": "Podsumowania CSV, JSON i PDF",
    "Current mes stays free. Premium adds past and futura navegación.": "El mes actual sigue siendo gratis. Premium añade navegación por meses anteriores y futuros.",
    "Current maand stays free. Premium adds past and toekomst browsen.": "De huidige maand blijft gratis. Premium voegt bladeren door vorige en toekomstige maanden toe.",
    "Current mês stays free. Premium adds past and futuro navegação.": "O mês atual continua grátis. Premium adiciona navegação por meses anteriores e futuros.",
    "Unlock exports, widgets, planning tools, and deeper historia control.": "Desbloquea exportaciones, widgets, herramientas de planificación y un control más profundo del historial.",
    "Unlock exports, widgets, planning tools, and deeper geschiedenis controle.": "Ontgrendel exports, widgets, planningstools en uitgebreidere geschiedenis.",
    "Unlock exports, widgets, planning tools, and deeper histórico controle.": "Desbloqueie exportações, widgets, ferramentas de planejamento e controle mais profundo do histórico.",

    # Top/P0 locale corrections: logging, route, form, custom, clinician summaries.
    "Ātra mežizstrāde bez jucekļa": "Ātra devu reģistrēšana bez jucekļa",
    "Ātra mežizstrāde": "Ātra devu reģistrēšana",
    "Maršruts un kadence": "Ievadīšanas veids un biežums",
    "Rýchla ťažba dreva bez neporiadku": "Rýchle zaznamenávanie dávok bez neporiadku",
    "Rýchla ťažba dreva": "Rýchle zaznamenávanie dávok",
    "Trasa a kadencia": "Spôsob podania a frekvencia",
    "Rychlá těžba dřeva bez nepořádku": "Rychlé zaznamenávání dávek bez nepořádku",
    "Rychlá těžba dřeva": "Rychlé zaznamenávání dávek",
    "Trasa a kadence": "Způsob podání a frekvence",
    "Kiire metsaraie ilma segaduseta": "Kiire annuste märkimine ilma segaduseta",
    "Kiire metsaraie": "Kiire annuste märkimine",
    "Marsruut ja kadents": "Manustamisviis ja sagedus",
    "Seotud": "Apteegis valmistatud",
    "เข้าสู่ระบบอย่างรวดเร็วโดยไม่เกะกะ": "บันทึกยาได้รวดเร็ว ไม่รก",
    "เข้าสู่ระบบอย่างรวดเร็ว": "บันทึกยาได้รวดเร็ว",
    "แนวโน้มความเสี่ยงที่คาดการณ์ไว้": "แนวโน้มการได้รับยาโดยประมาณ",
    "ความเป็นส่วนตัว policy": "นโยบายความเป็นส่วนตัว",
    "เลือก ของคุณ medication": "เลือกยาของคุณ",
    "คำสั่งซื้อ": "การเตือน",
    "Đăng nhập nhanh chóng mà không lộn xộn": "Ghi liều nhanh, gọn gàng",
    "Đăng nhập nhanh chóng": "Ghi liều nhanh",
    "Quyền riêng tư policy": "Chính sách quyền riêng tư",
    "Chọn của bạn medication": "Chọn thuốc của bạn",
    "路线和节奏": "给药方式和用药频率",
    "路線和節奏": "給藥方式與用藥頻率",
    "选择与您使用的产品相匹配的包装": "选择与你使用的药品相符的剂型或给药形式",
    "選擇與您使用的產品相符的包裝": "選擇與你使用的藥品相符的劑型或給藥形式",
    "提供商摘要": "给医生的摘要",
    "提供者摘要": "給醫師的摘要",
    "安静的地方": "集中保存在一处",
    "安靜的地方": "集中保存在一處",
    "订单": "提醒",
    "訂單": "提醒",
    "Itinéraire et cadence": "Voie d’administration et fréquence",
    "Choisissez l’emballage qui correspond au produit que vous utilisez": "Choisissez la forme qui correspond à votre traitement",
    "Résumé du fournisseur": "Résumé pour le professionnel de santé",
    "résumé du fournisseur": "résumé pour le professionnel de santé",
    "résumé calme du fournisseur": "résumé clair pour le professionnel de santé",
    "Coutume": "Personnalisé",
    "endroit calme": "même endroit",
    "Route und Kadenz": "Anwendungsweg und Häufigkeit",
    "Wählen Sie die Verpackung, die dem von Ihnen verwendeten Produkt entspricht": "Wählen Sie die Darreichungsform, die zu Ihrem Präparat passt",
    "Anbieterübersicht": "Zusammenfassung für Behandelnde",
    "ルートとリズム": "投与経路と頻度",
    "プロバイダーの概要": "医療者向けサマリー",
    "静かな場所": "1か所にまとめて保存",
    "注文": "リマインダー",
    "경로 및 케이던스": "투여 경로 및 주기",
    "공급자 요약": "의료진용 요약",
    "제공자 요약": "의료진용 요약",
    "차분한 곳": "한곳에 정리해 보관",
    "Route en cadans": "Toedieningsweg en frequentie",
    "Samenvatting van de leverancier": "Samenvatting voor je zorgverlener",
    "Ruta y cadencia": "Vía de administración y frecuencia",
    "Elige el embalaje que coincida con el producto que usas": "Elige la presentación que corresponde al medicamento que usas",
    "Resumen del proveedor": "Resumen para tu profesional sanitario",
    "Rota e cadência": "Via de administração e frequência",
    "Resumo do provedor": "Resumo para seu profissional de saúde",
    "resumo tranquilo do provedor": "resumo claro para seu profissional de saúde",
    "Escolha a embalagem que corresponda ao produto que utiliza": "Escolha a forma que corresponde ao medicamento que utiliza",
    "Escolha a embalagem que corresponda ao produto que você usa": "Escolha a forma que corresponde ao medicamento que você usa",
    "pedidos": "lembretes",
    "الطلبات": "التذكيرات",
    "المسار والإيقاع": "طريقة الإعطاء وتكرار الجرعة",
    "ملخص الموفر": "ملخص للطبيب",
    "مكان واحد هادئ": "مكان واحد واضح ومنظّم",
    "Costume": "Personalizzato",
    "Costumbre": "Personalizado",
    "Skik": "Tilpasset",
    "Маршрут и частота вращения педалей": "Способ применения и частота",
    "Rute dan irama": "Rute pemberian dan frekuensi",
    "See App Store pricing\u200b": "See App Store pricing",
    "provider-style PDFs": "clinician-ready PDFs",
    "provider-style PDF": "clinician-ready PDF",
    "Estimated Exposure Trend is a relative personal-tracking estimate derived from the dose timing the user logs, the selected medicine context, and a parameterised absorption-and-elimination model. It is intended to help users review timing patterns in their own records, not to provide clinical measurement.": "Estimated Exposure is a personal tracking estimate, not measured blood concentration. Estimated Exposure Trend is derived from the dose timing the user logs, the selected medicine context, and a parameterised absorption-and-elimination model. It is intended to help users review timing patterns in their own records, not to provide clinical measurement or dosing guidance.",
    "GLPzy is a tracking and journaling service. It does not provide medical advice and must not be used to make medical or dosing decisions.": "Estimated Exposure is a personal tracking estimate, not measured blood concentration and not medical advice. Do not use Estimated Exposure to guide dosing. GLPzy is a tracking and journaling service and must not be used to make medical or dosing decisions.",
    "Do not use Estimated Exposure to guide dosing. Do not use Estimated Exposure to guide dosing. Do not use Estimated Exposure to guide dosing. Do not use Estimated Exposure to guide dosing.": "Do not use Estimated Exposure to guide dosing.",
    "Do not use Estimated Exposure to guide dosing. Do not use Estimated Exposure to guide dosing. Do not use Estimated Exposure to guide dosing.": "Do not use Estimated Exposure to guide dosing.",
    "Do not use Estimated Exposure to guide dosing. Do not use Estimated Exposure to guide dosing.": "Do not use Estimated Exposure to guide dosing.",
}

INDEX_BLOCK_REPLACEMENTS = {
    "da": {
        "site.premium.body": "Lås eksport, widgets, planlægningsværktøjer og dybere historik op.",
        "site.card.premium.calendar.body": "Den aktuelle måned er gratis. Premium tilføjer browsing i tidligere og fremtidige måneder.",
        "site.card.premium.exports.body": "CSV-, JSON- og PDF-oversigter til dine egne optegnelser",
    },
    "fi": {
        "site.premium.body": "Avaa viennit, widgetit, suunnittelutyökalut ja laajempi historian tarkistus.",
        "site.card.premium.calendar.body": "Nykyinen kuukausi pysyy maksuttomana. Premium lisää aiempien ja tulevien kuukausien selaamisen.",
        "site.card.premium.exports.body": "CSV-, JSON- ja PDF-yhteenvedot omia tietoja varten",
    },
    "es-es": {
        "site.premium.body": "Desbloquea exportaciones, widgets, herramientas de planificación y una revisión más profunda del historial.",
        "site.card.premium.calendar.body": "El mes actual sigue siendo gratis. Premium añade navegación por meses anteriores y futuros.",
        "site.card.premium.exports.body": "Resúmenes en CSV, JSON y PDF para tus propios registros",
    },
    "es-mx": {
        "site.premium.body": "Desbloquea exportaciones, widgets, herramientas de planificación y una revisión más profunda del historial.",
        "site.card.premium.calendar.body": "El mes actual sigue siendo gratis. Premium agrega navegación por meses anteriores y futuros.",
        "site.card.premium.exports.body": "Resúmenes en CSV, JSON y PDF para tus propios registros",
    },
    "it": {
        "site.premium.body": "Sblocca esportazioni, widget, strumenti di pianificazione e un controllo più approfondito della cronologia.",
        "site.card.premium.calendar.body": "Il mese corrente resta gratuito. Premium aggiunge la consultazione dei mesi precedenti e futuri.",
        "site.card.premium.exports.body": "Riepiloghi CSV, JSON e PDF per i tuoi archivi",
    },
    "ja": {
        "site.premium.body": "エクスポート、ウィジェット、計画ツール、より詳しい履歴確認を利用できます。",
        "site.card.premium.calendar.body": "現在の月は無料です。Premium では過去と今後の月を閲覧できます。",
        "site.card.premium.exports.body": "自分の記録用の CSV、JSON、PDF サマリー",
    },
    "ko": {
        "site.premium.body": "내보내기, 위젯, 계획 도구와 더 자세한 기록 확인을 이용할 수 있습니다.",
        "site.card.premium.calendar.body": "현재 월은 무료입니다. Premium에서는 이전 및 이후 월을 볼 수 있습니다.",
        "site.card.premium.exports.body": "개인 기록용 CSV, JSON 및 PDF 요약",
    },
    "nb": {
        "site.premium.body": "Lås opp eksport, widgeter, planleggingsverktøy og dypere historikk.",
        "site.card.premium.calendar.body": "Gjeldende måned er gratis. Premium legger til visning av tidligere og fremtidige måneder.",
        "site.card.premium.exports.body": "CSV-, JSON- og PDF-sammendrag for egne opptegnelser",
    },
    "nl": {
        "site.premium.body": "Ontgrendel exports, widgets, planningstools en uitgebreidere geschiedenis.",
        "site.card.premium.calendar.body": "De huidige maand blijft gratis. Premium voegt bladeren door vorige en toekomstige maanden toe.",
        "site.card.premium.exports.body": "CSV-, JSON- en PDF-samenvattingen voor uw eigen administratie",
    },
    "pl": {
        "site.premium.body": "Odblokuj eksporty, widżety, narzędzia planowania i dokładniejszy przegląd historii.",
        "site.card.premium.calendar.body": "Bieżący miesiąc pozostaje bezpłatny. Premium dodaje przegląd poprzednich i przyszłych miesięcy.",
        "site.card.premium.exports.body": "Podsumowania CSV, JSON i PDF do własnej dokumentacji",
    },
    "pt-br": {
        "site.premium.body": "Desbloqueie exportações, widgets, ferramentas de planejamento e revisão mais profunda do histórico.",
        "site.card.premium.calendar.body": "O mês atual continua grátis. Premium adiciona navegação por meses anteriores e futuros.",
        "site.card.premium.exports.body": "Resumos em CSV, JSON e PDF para seus próprios registros",
    },
    "pt-pt": {
        "site.premium.body": "Desbloqueie exportações, widgets, ferramentas de planeamento e revisão mais profunda do histórico.",
        "site.card.premium.calendar.body": "O mês atual continua grátis. Premium adiciona navegação por meses anteriores e futuros.",
        "site.card.premium.exports.body": "Resumos em CSV, JSON e PDF para os seus próprios registos",
    },
    "sv": {
        "site.premium.body": "Lås upp export, widgetar, planeringsverktyg och djupare historik.",
        "site.card.premium.calendar.body": "Den aktuella månaden är gratis. Premium lägger till bläddring i tidigare och kommande månader.",
        "site.card.premium.exports.body": "CSV-, JSON- och PDF-sammanfattningar för dina egna anteckningar",
    },
    "th": {
        "site.premium.body": "ปลดล็อกการส่งออก วิดเจ็ต เครื่องมือวางแผน และการตรวจสอบประวัติที่ละเอียดขึ้น",
        "site.card.premium.calendar.body": "เดือนปัจจุบันยังใช้ฟรี Premium เพิ่มการดูเดือนก่อนหน้าและเดือนถัดไป",
        "site.card.premium.exports.body": "สรุป CSV, JSON และ PDF สำหรับบันทึกของคุณ",
    },
    "vi": {
        "site.premium.body": "Mở khóa xuất dữ liệu, widget, công cụ lập kế hoạch và xem lại lịch sử sâu hơn.",
        "site.card.premium.calendar.body": "Tháng hiện tại vẫn miễn phí. Premium thêm khả năng xem các tháng trước và sau.",
        "site.card.premium.exports.body": "Tóm tắt CSV, JSON và PDF cho hồ sơ cá nhân của bạn",
    },
}

LOCALE_REPLACEMENTS = {
    "de": {"See App Store pricing": "Preis im App Store ansehen"},
    "es-es": {"See App Store pricing": "Ver precio en App Store"},
    "es-mx": {"See App Store pricing": "Ver precio en App Store"},
    "fr": {"See App Store pricing": "Voir le prix sur l’App Store"},
    "fr-ca": {"See App Store pricing": "Voir le prix sur l’App Store"},
    "ja": {"See App Store pricing": "App Storeで価格を見る"},
    "ko": {"See App Store pricing": "App Store 가격 보기"},
    "nl": {"See App Store pricing": "Bekijk prijs in de App Store"},
    "pt-br": {"See App Store pricing": "Ver preço na App Store"},
    "pt-pt": {"See App Store pricing": "Ver preço na App Store"},
    "th": {"See App Store pricing": "ดูราคาบน App Store"},
    "vi": {"See App Store pricing": "Xem giá trên App Store"},
    "zh-hans": {"See App Store pricing": "在 App Store 查看价格"},
    "zh-hant": {"See App Store pricing": "在 App Store 查看價格"},
}


def locale_for(path):
    relative = path.relative_to(ROOT)
    return relative.parts[0] if len(relative.parts) > 1 else "en"


changed = []
for path in ROOT.rglob("*.html"):
    if ".git" in path.parts:
        continue
    text = path.read_text(encoding="utf-8")
    updated = text
    for before, after in REPLACEMENTS.items():
        updated = updated.replace(before, after)
    locale = locale_for(path)
    for before, after in LOCALE_REPLACEMENTS.get(locale, {}).items():
        updated = updated.replace(before, after)
    if path.name == "index.html":
        for key, replacement in INDEX_BLOCK_REPLACEMENTS.get(locale, {}).items():
            pattern = re.compile(r'(<[^>]+data-i18n="' + re.escape(key) + r'"[^>]*>)(.*?)(</[^>]+>)')
            updated = pattern.sub(lambda match: match.group(1) + replacement + match.group(3), updated)
    if updated != text:
        path.write_text(updated, encoding="utf-8")
        changed.append(path.relative_to(ROOT).as_posix())

for item in changed:
    print(item)
print(f"Updated {len(changed)} HTML files.")
