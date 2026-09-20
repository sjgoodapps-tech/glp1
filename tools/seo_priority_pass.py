#!/usr/bin/env python3
import json
import re
from datetime import date
from html import escape
from pathlib import Path
from urllib.parse import urlencode
from refresh_screenshots import figure as approved_figure, refreshed_html

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
FACTS = json.loads((DATA / "product-facts.json").read_text(encoding="utf-8"))
MANIFEST = json.loads((DATA / "screenshot-manifest.json").read_text(encoding="utf-8"))
REBRAND = json.loads((DATA / "rebrand.json").read_text(encoding="utf-8"))
REBRAND_PAGE = json.loads((DATA / "rebrand-page.json").read_text(encoding="utf-8"))
SITE = FACTS["site_url"].rstrip("/")
APP_STORE = FACTS["app_store_url"]
REVIEWED_ISO = FACTS["content_reviewed"]
REVIEWED_DATE = date.fromisoformat(REVIEWED_ISO)
REVIEWED_DISPLAY = f"{REVIEWED_DATE.day} {REVIEWED_DATE.strftime('%B %Y')}"
PUBLISHER = FACTS["publisher"]
PUBLISHER_TYPE = FACTS["publisher_type"]
PRIMARY_SOURCES = FACTS["primary_sources"]
SCHEMA_DESCRIPTION = "Private iPhone and iPad app for recording GLP-1 doses, weight, symptoms, photos and optional read-only Apple Health context. Personal tracking only."

SLOTS = {item["slot"]: item for item in MANIFEST["slots"]}
SOURCE_ASSETS = MANIFEST["source_assets"]
HERO_ASSETS = MANIFEST["priority_page_hero_assets"]
RESPONSIVE_WIDTHS = [360, 720, 1080, 1320]

CAMPAIGNS = {
    "site_default": ("siteDefault", "founding_site_default"),
    "seo_glp1_tracker": ("seoGlp1Tracker", "seo_glp1_tracker"),
    "seo_mounjaro_tracker": ("seoMounjaro", "seo_mounjaro_tracker"),
    "seo_wegovy_tracker": ("seoWegovy", "seo_wegovy_tracker"),
    "seo_zepbound_tracker": ("seoZepbound", "seo_zepbound_tracker"),
    "seo_tirzepatide_tracker": ("seoTirzepatide", "seo_tirzepatide_tracker"),
    "seo_semaglutide_tracker": ("seoSemaglutide", "seo_semaglutide_tracker"),
    "seo_side_effect_tracker": ("seoSideEffectTracker", "seo_side_effect_tracker"),
    "seo_photo_tracker": ("seoPhotoTracker", "seo_photo_tracker"),
    "seo_weight_tracker": ("seoWeightTracker", "seo_weight_tracker"),
    "seo_dose_reminder": ("seoDoseReminder", "seo_dose_reminder"),
    "seo_apple_health_injection": ("seoAppleHealthInjection", "seo_apple_health_injection"),
}

SOURCE_KEYS_BY_PAGE = {
    "glp1-weight-dose-symptom-tracker.html": ["apple_health_authorisation"],
    "mounjaro-tracker-iphone.html": ["mounjaro_label", "apple_health_authorisation"],
    "wegovy-tracker-iphone.html": ["wegovy_label", "apple_health_authorisation"],
    "zepbound-tracker-iphone.html": ["zepbound_label", "apple_health_authorisation"],
    "tirzepatide-tracker-iphone.html": ["mounjaro_label", "zepbound_label"],
    "semaglutide-tracker-iphone.html": ["wegovy_label"],
    "local-first-private-glp-tracker.html": ["apple_health_authorisation"],
    "glp1-dose-reminder-app.html": [],
    "glp1-side-effect-symptom-tracker.html": [],
    "glp1-weight-tracker.html": ["apple_health_authorisation"],
    "glp1-progress-photo-tracker.html": [],
    "apple-health-glp-tracker.html": ["apple_health_authorisation"],
}

COMMON_LINKS = [
    ("GLP-1 tracker app", "glp1-weight-dose-symptom-tracker.html"),
    ("Mounjaro tracker", "mounjaro-tracker-iphone.html"),
    ("Wegovy tracker", "wegovy-tracker-iphone.html"),
    ("Zepbound tracker", "zepbound-tracker-iphone.html"),
    ("Tirzepatide tracker", "tirzepatide-tracker-iphone.html"),
    ("Semaglutide tracker", "semaglutide-tracker-iphone.html"),
    ("Dose reminders", "glp1-dose-reminder-app.html"),
    ("Symptom tracker", "glp1-side-effect-symptom-tracker.html"),
    ("Weight tracker", "glp1-weight-tracker.html"),
    ("Progress photos", "glp1-progress-photo-tracker.html"),
    ("Apple Health", "apple-health-glp-tracker.html"),
    ("Privacy and no account", "local-first-private-glp-tracker.html"),
    ("Privacy policy", "privacy.html"),
    ("Data rights", "data-rights.html"),
    ("Medical safety", "medical-safety.html"),
    ("Methodology", "methodology.html"),
]

def campaign_url(token):
    params = {"ct": token}
    provider = FACTS["app_store_campaign"]["provider_token"]
    if provider:
        params.update(pt=str(provider), mt="8")
    return f"{APP_STORE}?{urlencode(params)}"


TRACKS = ", ".join(FACTS["supported_tracking_types"])

PAGES = {
    "glp1-weight-dose-symptom-tracker.html": {
        "family": "broad tracker",
        "title": "GLP-1 tracker app for iPhone | OneGLP",
        "description": "Track GLP-1 doses, reminders, injection sites, weight, symptoms, appetite, nutrition, photos and optional read-only Apple Health context privately on iPhone.",
        "h1": "GLP-1 tracker app for iPhone",
        "campaign": "seo_glp1_tracker",
        "answer": "OneGLP is a private GLP-1 tracker for iPhone and iPad. It records dose dates, reminders, injection sites, weight, symptoms, appetite, nutrition, notes, progress photos and optional read-only Apple Health context. It is for personal review only and does not give medical or dosing advice.",
        "intro": [
            "Use OneGLP when you want one place for the routine details that are easy to lose in notes, screenshots or calendar entries.",
            "The app supports personal tracking for Mounjaro, Wegovy, Zepbound, tirzepatide, semaglutide and other GLP-1 contexts without making treatment claims."
        ],
        "workflow": [
            "Set up the medicine context you want to record.",
            "Log doses, sites, reminders, weight, symptoms, appetite, nutrition, notes and photos as your own record.",
            "Review charts, timelines, exports and optional read-only Apple Health context when you need a clearer history."
        ],
        "does": ["keeps routine records together", "supports user-directed exports", "shows personal trend views", "keeps core tracking available without a mandatory in-app account"],
        "does_not": ["prescribe medicine", "recommend doses", "diagnose symptoms", "replace official medicine information", "replace advice from a qualified clinician"],
        "slots": MANIFEST['page_slots']['glp1-weight-dose-symptom-tracker.html'],
        "faq": [
            ("What can OneGLP track?", f"OneGLP can track {TRACKS}."),
            ("Does OneGLP tell me how much medicine to take?", "No. OneGLP is a tracking app. It does not provide dosing advice, prescribing advice or treatment instructions."),
            ("Do I need an account?", FACTS["no_account_claim"]),
            ("Can I use OneGLP with Mounjaro, Wegovy or Zepbound?", "Yes. OneGLP can keep personal records for those medicine contexts, with separate pages for each one."),
            ("Does OneGLP use Apple Health?", FACTS["apple_health_scope"]),
            ("Can I export my records?", FACTS["export_formats"]),
            ("Is Estimated Exposure a blood level?", "No. Estimated Exposure is a personal tracking estimate, not measured blood concentration and not for dosing decisions.")
        ],
    },
    "mounjaro-tracker-iphone.html": {
        "family": "medicine",
        "title": "Mounjaro tracker app for iPhone | OneGLP",
        "description": "Track Mounjaro doses, reminders, injection sites, weight, symptoms, photos and optional read-only Apple Health context privately on iPhone.",
        "h1": "Mounjaro tracker app for iPhone",
        "campaign": "seo_mounjaro_tracker",
        "answer": "OneGLP helps you keep a private Mounjaro tracking record on iPhone. You can log dose dates, reminders, injection sites, weight, symptoms, notes, progress photos and optional read-only Apple Health context. OneGLP is independent and does not give dosing advice.",
        "intro": ["Mounjaro is a brand name for tirzepatide. OneGLP is not affiliated with or endorsed by the medicine manufacturer.", "Use OneGLP to keep your own history for appointments, habit review and export. Always follow your clinician, pharmacist and official product information."],
        "workflow": ["Record each dose date and site.", "Add weight, symptom, appetite, nutrition and photo context when useful.", "Export or review your own record before an appointment."],
        "does": ["tracks Mounjaro context as personal records", "keeps photos and notes beside dose history", "supports export for your own review"],
        "does_not": ["provide Mounjaro dosing advice", "interpret symptoms", "replace official Mounjaro information"],
        "slots": MANIFEST['page_slots']['mounjaro-tracker-iphone.html'],
        "faq": [
            ("Can I use OneGLP as a Mounjaro tracker?", "Yes. OneGLP can track Mounjaro dose records, reminders, sites, symptoms, weight, notes and photos for personal review."),
            ("Does OneGLP give Mounjaro dosing advice?", "No. OneGLP does not provide dosing advice or treatment instructions."),
            ("Can I track side-effect notes?", "Yes. You can record symptom and side-effect notes for your own record."),
            ("Can I connect Apple Health?", FACTS["apple_health_scope"]),
            ("Can I export records for an appointment?", FACTS["export_formats"]),
            ("Is OneGLP affiliated with Mounjaro?", "No. OneGLP is independent and is not affiliated with or endorsed by the medicine manufacturer.")
        ],
    },
    "wegovy-tracker-iphone.html": {
        "family": "medicine",
        "title": "Wegovy tracker app for iPhone | OneGLP",
        "description": "Track Wegovy doses, reminders, weight, symptoms, photos and optional read-only Apple Health context privately on iPhone.",
        "h1": "Wegovy tracker app for iPhone",
        "campaign": "seo_wegovy_tracker",
        "answer": "OneGLP helps you track Wegovy routines privately on iPhone. You can log dose dates, reminders, injection sites, weight, symptoms, appetite, notes, progress photos and optional read-only Apple Health context. OneGLP is for personal review and does not tell you how to dose.",
        "intro": ["Wegovy is a brand name for semaglutide. OneGLP is not affiliated with or endorsed by the medicine manufacturer.", "Use OneGLP to keep weight, dose, symptom and photo records together so you can review your own history without scattered notes."],
        "workflow": ["Record dose dates and reminder context.", "Review weight and symptom notes beside dose stages.", "Use exports or photo comparison when you want a clearer personal record."],
        "does": ["tracks Wegovy context as personal records", "shows weight and photo history", "supports optional read-only Apple Health context"],
        "does_not": ["provide Wegovy dosing advice", "set clinical weight goals", "diagnose symptoms"],
        "slots": MANIFEST['page_slots']['wegovy-tracker-iphone.html'],
        "faq": [
            ("Can I use OneGLP as a Wegovy tracker?", "Yes. OneGLP can track Wegovy dose records, reminders, weight, symptoms and photos for personal review."),
            ("Does OneGLP provide Wegovy dosing advice?", "No. OneGLP is not a dosing guide and does not provide treatment instructions."),
            ("Can I track weight beside doses?", "Yes. Weight records can be reviewed beside dose history and other context."),
            ("Can I use Apple Health weight data?", FACTS["apple_health_scope"]),
            ("Can I export my Wegovy tracking history?", FACTS["export_formats"]),
            ("Is OneGLP affiliated with Wegovy?", "No. OneGLP is independent and is not affiliated with or endorsed by the medicine manufacturer.")
        ],
    },
    "zepbound-tracker-iphone.html": {
        "family": "medicine",
        "title": "Zepbound tracker app for iPhone | OneGLP",
        "description": "Track Zepbound doses, reminders, injection sites, weight, symptoms, photos and optional read-only Apple Health context privately on iPhone.",
        "h1": "Zepbound tracker app for iPhone",
        "campaign": "seo_zepbound_tracker",
        "answer": "OneGLP helps you keep a private Zepbound tracking record on iPhone. You can log dose dates, reminders, injection sites, weight, symptoms, notes, progress photos and optional read-only Apple Health context. OneGLP is independent and does not provide dosing advice.",
        "intro": ["Zepbound is a brand name for tirzepatide. OneGLP is not affiliated with or endorsed by the medicine manufacturer.", "Use OneGLP for your own records and appointment preparation. It does not replace clinician instructions, pharmacy advice or official product information."],
        "workflow": ["Record dose dates, reminder times and injection sites.", "Add weight, symptom, appetite, nutrition, note and photo context when useful.", "Review charts, exports and the methodology page when you need to understand personal tracking estimates."],
        "does": ["keeps Zepbound context in a private record", "supports injection-site and reminder review", "connects dose history with weight, symptoms and photos", "links Estimated Exposure wording to the methodology page"],
        "does_not": ["provide Zepbound dosing advice", "interpret side effects", "replace official Zepbound information", "measure blood concentration"],
        "slots": MANIFEST['page_slots']['zepbound-tracker-iphone.html'],
        "faq": [
            ("Can I use OneGLP as a Zepbound tracker?", "Yes. OneGLP can track Zepbound dose records, reminders, sites, symptoms, weight, notes and photos for personal review."),
            ("Does OneGLP provide Zepbound dosing advice?", "No. OneGLP does not provide dosing advice or treatment instructions."),
            ("Can I track injection sites?", "Yes. You can log injection sites beside dose dates and notes."),
            ("Can I review progress photos?", "Yes. Progress photo tools help you review your own visual history."),
            ("Can I export records?", FACTS["export_formats"]),
            ("Is Estimated Exposure a blood level?", "No. Estimated Exposure is a personal tracking estimate, not measured blood concentration and not for dosing decisions."),
            ("Is OneGLP affiliated with Zepbound?", "No. OneGLP is independent and is not affiliated with or endorsed by the medicine manufacturer.")
        ],
    },
    "tirzepatide-tracker-iphone.html": {
        "family": "ingredient",
        "title": "Tirzepatide tracker app for iPhone | OneGLP",
        "description": "Track tirzepatide dose records, reminders, weight, symptoms, photos and optional read-only Apple Health context privately on iPhone.",
        "h1": "Tirzepatide tracker app for iPhone",
        "campaign": "seo_tirzepatide_tracker",
        "answer": "OneGLP is a private tirzepatide tracker for iPhone and iPad. It can record dose dates, reminder times, injection sites, weight, symptoms, notes, photos and optional read-only Apple Health context. It is for personal review only and does not guide dosing.",
        "intro": ["Tirzepatide is the ingredient used in some GLP-1 and GIP medicine contexts. OneGLP supports personal tracking records without making treatment claims.", "Use the app to review your own routine, not to decide whether to start, stop, skip, delay or change a dose."],
        "workflow": ["Choose the medicine context you want to record.", "Log dose, site, reminder, symptom, weight and photo records.", "Review related Mounjaro and Zepbound pages for brand-context tracking notes."],
        "does": ["tracks tirzepatide context as personal data", "links brand pages and ingredient context", "supports export for user records"],
        "does_not": ["provide treatment instructions", "recommend dose changes", "measure medicine levels"],
        "slots": MANIFEST['page_slots']['tirzepatide-tracker-iphone.html'],
        "faq": [
            ("Can I track tirzepatide in OneGLP?", "Yes. OneGLP can keep dose, reminder, site, weight, symptom, note and photo records for personal review."),
            ("Does OneGLP support Mounjaro and Zepbound contexts?", "Yes. OneGLP has separate pages for Mounjaro and Zepbound tracking contexts."),
            ("Does OneGLP provide dosing advice?", "No. OneGLP is not a dosing guide and does not provide treatment instructions."),
            ("What exports are available?", FACTS["export_formats"]),
            ("Is Apple Health required?", "No. Apple Health is optional and read-only."),
            ("Is Estimated Exposure a clinical measurement?", "No. Estimated Exposure is not measured blood concentration.")
        ],
    },
    "semaglutide-tracker-iphone.html": {
        "family": "ingredient",
        "title": "Semaglutide tracker app for iPhone | OneGLP",
        "description": "Track semaglutide dose records, reminders, weight, symptoms, photos and optional read-only Apple Health context privately on iPhone.",
        "h1": "Semaglutide tracker app for iPhone",
        "campaign": "seo_semaglutide_tracker",
        "answer": "OneGLP is a private semaglutide tracker for iPhone and iPad. It can record dose dates, reminders, injection sites, weight, symptoms, appetite, notes, photos and optional read-only Apple Health context. It is for personal review only and does not guide dosing.",
        "intro": ["Semaglutide is used in several medicine contexts. OneGLP supports private tracking records without making treatment or availability claims.", "Use OneGLP to keep routine records together and export your own history when needed."],
        "workflow": ["Record semaglutide-context dose history.", "Review weight, symptoms, appetite, nutrition and photo records together.", "Use related Wegovy and Ozempic pages where brand context matters."],
        "does": ["tracks semaglutide context as personal records", "supports weight, symptom and photo review", "keeps Apple Health optional and read-only"],
        "does_not": ["provide semaglutide dosing advice", "diagnose symptoms", "make treatment claims"],
        "slots": MANIFEST['page_slots']['semaglutide-tracker-iphone.html'],
        "faq": [
            ("Can I track semaglutide in OneGLP?", "Yes. OneGLP can track semaglutide dose records, reminders, weight, symptoms, notes and photos."),
            ("Does OneGLP support Wegovy context?", "Yes. OneGLP has a separate Wegovy tracker page for that brand context."),
            ("Does OneGLP provide dosing advice?", "No. OneGLP is a personal tracking app, not a dosing guide."),
            ("Can I use Apple Health?", FACTS["apple_health_scope"]),
            ("Can I export records?", FACTS["export_formats"]),
            ("Is OneGLP affiliated with semaglutide medicine brands?", "No. OneGLP is independent and is not endorsed by medicine manufacturers.")
        ],
    },
    "local-first-private-glp-tracker.html": {
        "family": "privacy",
        "title": "Private GLP-1 tracker with no account required | OneGLP",
        "description": "Use OneGLP as a private local-first GLP-1 tracker with no mandatory in-app account, on-device records, exports, local backups and optional read-only Apple Health.",
        "h1": "Private GLP-1 tracker with no account required",
        "campaign": "site_default",
        "answer": "OneGLP is a local-first GLP-1 tracker. Core tracking works without a mandatory in-app account. Your records are kept on your device unless you export, share or restore a local backup. Optional Apple Health support is read-only and does not write data back.",
        "intro": ["You do not need to create an in-app account to record doses, weight, symptoms, reminders or photos.", "Exports and local backups are user-directed. You choose when to create a file, share it or restore it."],
        "workflow": ["Record core tracking data on the device.", "Export or back up records only when you choose.", "Review privacy, data rights and support pages for the policy details."],
        "does": ["keeps core tracking local-first", "supports user-directed exports and local backups", "keeps Apple Health optional and read-only"],
        "does_not": ["require a mandatory in-app account for core tracking", "create public profiles", "write data back to Apple Health"],
        "slots": MANIFEST['page_slots']['local-first-private-glp-tracker.html'],
        "faq": [
            ("Do I need an account to use OneGLP?", FACTS["no_account_claim"]),
            ("Where are my records kept?", FACTS["privacy_posture"]),
            ("Does Apple Health change that?", "No. Apple Health support is optional and read-only."),
            ("Can I export my records?", FACTS["export_formats"]),
            ("Can I restore a backup?", "Local backup and restore are user-directed tools."),
            ("Where can I read the privacy policy?", "Use the privacy, data rights and support pages linked on this site.")
        ],
    },
    "glp1-dose-reminder-app.html": {
        "family": "feature",
        "title": "GLP-1 dose reminder app for iPhone | OneGLP",
        "description": "Track GLP-1 dose dates, next dose reminders, last dose history, injection sites, weight, symptoms and notes privately on iPhone.",
        "h1": "GLP-1 dose reminder app for iPhone",
        "campaign": "seo_dose_reminder",
        "answer": "OneGLP helps you keep GLP-1 dose dates, reminder times, last dose history, injection sites and notes in one private iPhone app. It can support your routine record, but it does not change your schedule or tell you when to dose.",
        "intro": ["Dose reminders are easiest to trust when they sit beside the record of what happened last time.", "OneGLP keeps next dose, last dose, reminder time, injection site and routine notes together for personal review."],
        "workflow": ["Set the medicine context and reminder time you want to record.", "Log the dose when it happens, including site and notes if useful.", "Use supply or reorder planning only as a personal planning aid, not as dose guidance."],
        "does": ["records next dose and last dose context", "keeps reminder time and injection site history", "supports supply planning boundaries", "keeps reminders separate from clinical instructions"],
        "does_not": ["tell you when to take medicine", "change your prescribed schedule", "provide dosing advice", "replace clinician or pharmacy instructions"],
        "slots": MANIFEST['page_slots']['glp1-dose-reminder-app.html'],
        "faq": [
            ("Can OneGLP remind me about a dose?", "OneGLP can help track reminder times and next dose context for personal routine tracking."),
            ("Can I review the last dose?", "Yes. You can review last dose history, sites and notes."),
            ("Does OneGLP change my dose schedule?", "No. OneGLP does not provide dosing advice or schedule changes."),
            ("Can I track injection sites?", "Yes. Injection site records can sit beside dose records."),
            ("Can OneGLP help with supply or reorder planning?", "It can support personal planning context where available, but it does not change dose instructions or pharmacy advice."),
            ("Is this available without an account?", FACTS["no_account_claim"])
        ],
    },
    "glp1-side-effect-symptom-tracker.html": {
        "family": "feature",
        "title": "GLP-1 side effect and symptom tracker app | OneGLP",
        "description": "Track GLP-1 symptoms, side-effect notes, doses, weight, appetite, nutrition and progress photos privately on iPhone with OneGLP.",
        "h1": "GLP-1 side effect and symptom tracker",
        "campaign": "seo_side_effect_tracker",
        "answer": "OneGLP lets you record GLP-1 symptoms and side-effect notes beside doses, weight, appetite, nutrition and photos. It gives you a private record for review. It does not diagnose symptoms, explain side effects or provide medical advice.",
        "intro": ["Symptom tracking works best when it is plain and consistent.", "OneGLP keeps symptom notes close to the dose, weight, appetite and nutrition context you already record."],
        "workflow": ["Log symptoms or side-effect notes when you want a record.", "Add appetite, nutrition, dose and weight context without asking the app to interpret it.", "Export records or create a PDF summary for your clinician for appointments if needed."],
        "does": ["records symptoms and appetite notes", "keeps dose and weight context nearby", "supports export and appointment summaries"],
        "does_not": ["diagnose symptoms", "explain side effects", "triage urgent issues", "replace medical advice"],
        "slots": MANIFEST['page_slots']['glp1-side-effect-symptom-tracker.html'],
        "faq": [
            ("Can I track GLP-1 symptoms in OneGLP?", "Yes. You can record symptom and side-effect notes for personal review."),
            ("Does OneGLP tell me what symptoms mean?", "No. OneGLP does not diagnose or interpret symptoms."),
            ("Can I export symptom records?", FACTS["export_formats"]),
            ("Can I review symptoms with weight?", "Yes. Symptoms can be reviewed beside weight and other records."),
            ("Can I include appetite and nutrition context?", "Yes. Appetite and nutrition notes can sit beside symptoms and dose context."),
            ("Is OneGLP medical advice?", "No. OneGLP is for personal tracking only.")
        ],
    },
    "glp1-weight-tracker.html": {
        "family": "feature",
        "title": "GLP-1 weight tracker app for iPhone | OneGLP",
        "description": "Track GLP-1 weight history, dose records, symptoms, photos and optional read-only Apple Health context privately on iPhone.",
        "h1": "GLP-1 weight tracker app for iPhone",
        "campaign": "seo_weight_tracker",
        "answer": "OneGLP helps you track weight history beside GLP-1 dose records, symptoms, appetite, nutrition and progress photos. Optional Apple Health support can add read-only weight context. OneGLP is for personal review and does not judge progress or give treatment advice.",
        "intro": ["Weight records are easier to review when they sit beside dose dates, routine notes and photos.", "OneGLP can use manual entries and optional read-only Apple Health context where you grant permission."],
        "workflow": ["Record weight manually or use optional read-only Apple Health context.", "Review weight beside dose stages, symptoms, appetite, nutrition and photos.", "Export records for your own files or appointment preparation."],
        "does": ["tracks manual weight records", "can read Apple Health weight context with permission", "shows charts and dose-stage review", "supports export"],
        "does_not": ["set clinical goals", "judge progress", "tell you to change treatment", "write data back to Apple Health"],
        "slots": MANIFEST['page_slots']['glp1-weight-tracker.html'],
        "faq": [
            ("Can I track weight in OneGLP?", "Yes. You can track weight history beside dose and symptom records."),
            ("Can Apple Health add weight data?", FACTS["apple_health_scope"]),
            ("Does OneGLP judge my progress?", "No. OneGLP records and shows your data for personal review."),
            ("Can I export weight records?", FACTS["export_formats"]),
            ("Can I review weight with photos?", "Yes. Weight and photo history can be reviewed together."),
            ("Does OneGLP set clinical goals?", "No. It does not set clinical goals or give treatment advice.")
        ],
    },
    "glp1-progress-photo-tracker.html": {
        "family": "feature",
        "title": "GLP-1 progress photo tracker app | OneGLP",
        "description": "Track GLP-1 progress photos, weight, doses, symptoms and milestones privately on iPhone with OneGLP photo comparison tools.",
        "h1": "GLP-1 progress photo tracker",
        "campaign": "seo_photo_tracker",
        "answer": "OneGLP lets you keep GLP-1 progress photos beside dose history, weight records, symptoms and notes. Free includes 2 new photo uploads per month, while Premium includes unlimited photo uploads. Photo comparison is for personal review only. It does not assess health, diagnose changes or provide medical advice.",
        "intro": ["Progress photos can help you review visible changes alongside routine records.", "OneGLP keeps photo review tied to the same private tracking history as dose, weight and symptom logs."],
        "workflow": ["Save private progress photos when you choose.", "Compare photos beside weight, dose and note context.", "Use face-cover and sharing choices before any user-directed export."],
        "does": ["stores private photo records", "supports comparison and montage-style review", "keeps weight and dose context nearby", "lets the user choose export or sharing"],
        "does_not": ["assess health from photos", "diagnose body changes", "share photos automatically", "replace medical review"],
        "slots": MANIFEST['page_slots']['glp1-progress-photo-tracker.html'],
        "faq": [
            ("Can I track progress photos in OneGLP?", "Yes. OneGLP includes progress photo tracking and comparison tools."),
            ("How many progress photos can I upload for free?", f"{FACTS['free_photo_allowance']} Premium includes unlimited photo uploads."),
            ("Can I review photos beside weight?", "Yes. Photos can be reviewed with weight and dose records."),
            ("Does OneGLP assess my photos?", "No. Photos are for personal review only."),
            ("Can I cover my face before sharing?", "OneGLP supports user-directed photo review and export choices, including privacy choices where available."),
            ("Can I export records?", FACTS["export_formats"]),
            ("Do I need an account?", FACTS["no_account_claim"])
        ],
    },
    "apple-health-glp-tracker.html": {
        "family": "feature",
        "title": "Apple Health GLP-1 tracker support | OneGLP",
        "description": "Use OneGLP with optional read-only Apple Health data for weight, height, glucose, body, movement, workouts and nutrition context on iPhone.",
        "h1": "Apple Health GLP-1 tracker support",
        "campaign": "seo_apple_health_injection",
        "answer": "OneGLP can use optional read-only Apple Health context for GLP-1 tracking. With permission, it can read weight, height, glucose, body composition, movement, workouts and nutrition context. OneGLP does not write data back to Apple Health.",
        "intro": ["Apple Health is optional. Manual tracking remains the main record in OneGLP.", "Read-only Health context can help you review dose, weight, symptom and nutrition records together."],
        "workflow": ["Grant Apple Health permissions only if you want read-only context.", "Review Health context beside manual OneGLP records.", "Change permissions in iOS settings whenever needed."],
        "does": ["reads approved Health context", "keeps Health optional", "does not write back to Apple Health"],
        "does_not": ["require Apple Health", "change Health data", "provide clinical interpretation"],
        "slots": MANIFEST['page_slots']['apple-health-glp-tracker.html'],
        "faq": [
            ("Is Apple Health required?", "No. Apple Health is optional."),
            ("Is Apple Health read-only?", "Yes. OneGLP reads permitted Apple Health context and does not write data back."),
            ("What Apple Health data can be used?", "With permission, OneGLP can use weight, height, glucose, body composition, movement, workout and nutrition context."),
            ("Can I disconnect Apple Health?", "Apple Health permissions can be changed in iOS settings."),
            ("Does Apple Health change medical safety?", "No. OneGLP remains a personal tracking app and not medical advice.")
        ],
    },
}


def rel_url(path):
    return f"{SITE}/" if path == "index.html" else f"{SITE}/{path}"


def facts_table():
    rows = [
        ("App name", FACTS["app_name"]),
        ("Platform", FACTS["platform"]),
        ("Category", FACTS["category"]),
        ("Tracks", TRACKS),
        ("Account requirement", FACTS["no_account_claim"]),
        ("Privacy posture", FACTS["privacy_posture"]),
        ("Apple Health scope", FACTS["apple_health_scope"]),
        ("Export formats", FACTS["export_formats"]),
        ("Medical boundary", FACTS["medical_boundary"]),
        ("App Store link", f'<a data-app-store-link href="{APP_STORE}">OneGLP on the App Store</a>'),
    ]
    body = []
    for key, value in rows:
        cell = value if key == "App Store link" else escape(value)
        body.append(f'              <tr><th scope="row">{escape(key)}</th><td>{cell}</td></tr>')
    return "          <table class=\"seo-facts-table\" data-seo-facts>\n            <tbody>\n" + "\n".join(body) + "\n            </tbody>\n          </table>"


def campaign_details(page):
    return CAMPAIGNS[page["campaign"]]


def cta(page, label="Get OneGLP", placement="content"):
    key, token = campaign_details(page)
    return (
        f'<a class="button button-primary" data-app-store-link data-app-store-style="text" '
        f'data-app-store-campaign="{escape(key)}" data-cta-placement="{escape(placement)}" '
        f'href="{escape(campaign_url(token))}">{escape(label)}</a>'
    )




def screenshot_figure(slot_name):
    return approved_figure(slot_name)


def list_items(items):
    return "\n".join(f"            <li>{escape(item)}</li>" for item in items)


def source_section(path):
    source_items = []
    for key in SOURCE_KEYS_BY_PAGE[path]:
        item = PRIMARY_SOURCES[key]
        source_items.append(f'          <li><a href="{escape(item["url"])}">{escape(item["label"])}</a></li>')
    source_items.extend(
        [
            '          <li><a href="medical-safety.html">OneGLP medical safety boundaries</a></li>',
            '          <li><a href="methodology.html">OneGLP Estimated Exposure methodology</a></li>',
        ]
    )
    return f"""        <div class="seo-copy seo-evidence" data-seo-evidence>
          <h2>Sources and page information</h2>
          <p>Reviewed {REVIEWED_DISPLAY}. Published by {escape(PUBLISHER)}.</p>
          <ul>
{chr(10).join(source_items)}
          </ul>
          <p class="small">Official medicine information is linked for reference. OneGLP does not replace product information, prescribing instructions or advice from a qualified clinician.</p>
        </div>"""


def render_module(path, page):
    intro = "\n".join(f"          <p>{escape(p)}</p>" for p in page["intro"])
    workflow = list_items(page["workflow"])
    does = list_items(page["does"])
    does_not = list_items(page["does_not"])
    screenshots = "\n".join(screenshot_figure(slot) for slot in page["slots"])
    faq = "\n".join(f"          <details><summary>{escape(q)}</summary><p>{escape(a)}</p></details>" for q, a in page["faq"])
    links = "\n".join(f'          <a href="{href}">{escape(label)}</a>' for label, href in COMMON_LINKS)
    return f"""
    <section class="section-strip seo-answer-strip" data-seo-module>
      <div class="shell narrow-shell">
        <div class="section-head section-head-center">
          <div class="kicker">Direct answer</div>
          <h2>{escape(page["h1"])}</h2>
        </div>
        <div class="card seo-answer-card" data-seo-answer>
          <p>{escape(page["answer"])}</p>
          <div class="site-cta-actions">{cta(page, "Get OneGLP", "answer")}</div>
        </div>
        <div class="seo-copy">
{intro}
          <h2>How it works</h2>
          <ol>
{workflow}
          </ol>
          <div class="landing-grid">
            <div class="feature-card">
              <h3>What OneGLP does</h3>
              <ul>
{does}
              </ul>
            </div>
            <div class="feature-card">
              <h3>What OneGLP does not do</h3>
              <ul>
{does_not}
              </ul>
            </div>
          </div>
          <p data-seo-safety><strong>Safety boundary:</strong> <a href="methodology.html">Estimated Exposure</a> is a personal tracking estimate, not measured blood concentration and not medical advice. Do not use Estimated Exposure to guide dosing. Always check with your clinician before making medical decisions. Read the <a href="medical-safety.html">medical safety page</a>.</p>
        </div>
{facts_table()}
{source_section(path)}
        <div class="website-shot-grid" data-seo-screenshots>
{screenshots}
        </div>
        <div class="section-head section-head-center">
          <div class="kicker">FAQ</div>
          <h2>Common questions</h2>
        </div>
        <div class="faq-mini" data-seo-faq>
{faq}
        </div>
        <div class="meta-links" data-seo-related>
{links}
        </div>
        <div class="site-cta-actions seo-bottom-cta">{cta(page, "Get OneGLP on the App Store", "bottom")}</div>
      </div>
    </section>
"""


def schema_graph(path, page):
    url = rel_url(path)
    graph = [
        {"@type": PUBLISHER_TYPE, "@id": f"{SITE}/#publisher", "name": PUBLISHER, "url": f"{SITE}/"},
        {"@type": "WebSite", "@id": f"{SITE}/#website", "name": "OneGLP", "url": f"{SITE}/"},
        {
            "@type": "SoftwareApplication",
            "@id": f"{SITE}/#software",
            "name": "OneGLP",
            "alternateName": REBRAND['previous_name'],
            "subjectOf": {"@id": f"{SITE}/{REBRAND_PAGE['slug']}/#webpage"},
            "applicationCategory": "HealthApplication",
            "operatingSystem": "iOS",
            "url": f"{SITE}/",
            "downloadUrl": APP_STORE,
            "description": SCHEMA_DESCRIPTION,
            "publisher": {"@id": f"{SITE}/#publisher"},
            "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"},
        },
        {
            "@type": "WebPage",
            "@id": f"{url}#webpage",
            "url": url,
            "name": page["title"],
            "description": page["description"],
            "isPartOf": {"@id": f"{SITE}/#website"},
            "about": {"@id": f"{SITE}/#software"},
            "author": {"@id": f"{SITE}/#publisher"},
            "publisher": {"@id": f"{SITE}/#publisher"},
            "dateModified": REVIEWED_ISO,
        },
        {
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{SITE}/"},
                {"@type": "ListItem", "position": 2, "name": page["h1"], "item": url},
            ],
        },
        {
            "@type": "FAQPage",
            "mainEntity": [
                {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}}
                for q, a in page["faq"]
            ],
        },
    ]
    for slot_name in page["slots"]:
        slot = SLOTS[slot_name]
        graph.append({
            "@type": "ImageObject",
            "url": f"{SITE}/assets/responsive/seo-{Path(SOURCE_ASSETS[slot_name]).stem}-1320.webp",
            "caption": slot["caption"],
            "description": slot["alt"],
            "width": slot["width"],
            "height": slot["height"],
        })
    return '<script type="application/ld+json" data-seo-schema="true">\n' + json.dumps({"@context": "https://schema.org", "@graph": graph}, indent=2) + "\n  </script>"


def methodology_schema():
    graph = {
        "@context": "https://schema.org",
        "@graph": [
            {"@type": PUBLISHER_TYPE, "@id": f"{SITE}/#publisher", "name": PUBLISHER, "url": f"{SITE}/"},
            {"@type": "WebSite", "@id": f"{SITE}/#website", "name": "OneGLP", "url": f"{SITE}/"},
            {
                "@type": "TechArticle",
                "@id": f"{SITE}/methodology.html#article",
                "headline": "OneGLP methodology and Estimated Exposure Trend",
                "description": "Plain-language methodology for OneGLP chart estimates, Estimated Exposure Trend, assumptions and safety limits.",
                "url": f"{SITE}/methodology.html",
                "about": "Estimated Exposure Trend in OneGLP",
                "isPartOf": {"@id": f"{SITE}/#website"},
                "author": {"@id": f"{SITE}/#publisher"},
                "publisher": {"@id": f"{SITE}/#publisher"},
                "dateModified": REVIEWED_ISO,
            },
            {
                "@type": "BreadcrumbList",
                "itemListElement": [
                    {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{SITE}/"},
                    {"@type": "ListItem", "position": 2, "name": "Methodology", "item": f"{SITE}/methodology.html"},
                ],
            },
        ],
    }
    return '<script type="application/ld+json" data-seo-schema="true">\n' + json.dumps(graph, indent=2) + "\n  </script>"


def replace_or_insert(pattern, repl, text, before="</head>", flags=re.S | re.I):
    if re.search(pattern, text, flags):
        return re.sub(pattern, repl, text, count=1, flags=flags)
    return text.replace(before, f"  {repl}\n{before}", 1)


def update_meta(text, page, path):
    url = rel_url(path)
    title = escape(page["title"])
    desc = escape(page["description"])
    text = replace_or_insert(r"<title>.*?</title>", f"<title>{title}</title>", text)
    text = replace_or_insert(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{desc}">', text)
    text = replace_or_insert(r'<meta name="robots" content="[^"]*">', '<meta name="robots" content="index,follow">', text)
    text = replace_or_insert(r'<link rel="canonical" href="[^"]*">', f'<link rel="canonical" href="{url}">', text)
    for prop, value in [
        ("og:title", page["title"]),
        ("og:description", page["description"]),
        ("og:url", url),
        ("og:image", f"{SITE}/{REBRAND['share_image']}"),
    ]:
        text = replace_or_insert(rf'<meta property="{re.escape(prop)}" content="[^"]*">', f'<meta property="{prop}" content="{escape(value)}">', text)
    for name, value in [
        ("twitter:card", "summary_large_image"),
        ("twitter:title", page["title"]),
        ("twitter:description", page["description"]),
    ]:
        text = replace_or_insert(rf'<meta name="{re.escape(name)}" content="[^"]*">', f'<meta name="{name}" content="{escape(value)}">', text)
    text = re.sub(r"(<h1[^>]*>).*?(</h1>)", r"\1" + escape(page["h1"]) + r"\2", text, count=1, flags=re.S | re.I)
    return text


def strip_old_schema(text):
    return re.sub(r'\n\s*<script type="application/ld\+json"[^>]*>.*?</script>', "", text, flags=re.S | re.I)


def inject_schema(text, schema):
    anchor = '  <script defer src="site-config.js"></script>'
    if anchor in text:
        return text.replace(anchor, f"  {schema}\n{anchor}", 1)
    return text.replace("</head>", f"  {schema}\n</head>", 1)


def replace_module(text, module):
    if 'data-seo-module' in text:
        return re.sub(
            r'\n\s*<section class="section-strip seo-answer-strip" data-seo-module>.*?</section>',
            "\n" + module.rstrip(),
            text,
            count=1,
            flags=re.S | re.I,
        )
    return text.replace("</main>", module + "</main>", 1)


def strip_legacy_faq(text):
    return re.sub(
        r'\n\s*<section class="section-strip faq-strip">.*?</section>',
        "",
        text,
        flags=re.S | re.I,
    )


def rewrite_hero_image(text, path):
    return refreshed_html(path, text)




def rewrite_hero_campaign(text, page):
    hero = re.search(r'<section class="hero marketing-hero">.*?</section>', text, re.S | re.I)
    if not hero:
        return text
    key, token = campaign_details(page)
    segment = hero.group(0)

    def update_anchor(match):
        tag = match.group(0)
        if re.search(r'\bdata-app-store-campaign="[^"]*"', tag, re.I):
            tag = re.sub(
                r'\bdata-app-store-campaign="[^"]*"',
                f'data-app-store-campaign="{key}"',
                tag,
                count=1,
                flags=re.I,
            )
        else:
            tag = tag[:-1] + f' data-app-store-campaign="{key}">'
        if re.search(r'\bhref="[^"]*"', tag, re.I):
            tag = re.sub(r'\bhref="[^"]*"', f'href="{escape(campaign_url(token))}"', tag, count=1, flags=re.I)
        if "data-cta-placement=" not in tag:
            tag = tag[:-1] + ' data-cta-placement="hero">'
        return tag

    segment = re.sub(
        r'<a\b(?=[^>]*\bdata-app-store-link\b)[^>]*>',
        update_anchor,
        segment,
        count=1,
        flags=re.I,
    )
    return text[:hero.start()] + segment + text[hero.end():]


def ensure_priority_image_attrs(text):
    def fix(match):
        tag = match.group(0)
        if " width=" not in tag:
            tag = tag[:-1] + ' width="1320" height="2868">'
        if " alt=" not in tag:
            tag = tag[:-1] + ' alt="OneGLP app screenshot.">'
        if " decoding=" not in tag:
            tag = tag[:-1] + ' decoding="async">'
        if " loading=" not in tag and "fetchpriority=" not in tag:
            tag = tag[:-1] + ' loading="lazy">'
        return tag
    return re.sub(r"<img\b[^>]*>", fix, text, flags=re.I)


def update_priority_page(path, page):
    file = ROOT / path
    text = file.read_text(encoding="utf-8")
    text = update_meta(text, page, path)
    text = strip_old_schema(text)
    text = inject_schema(text, schema_graph(path, page))
    text = strip_legacy_faq(text)
    text = replace_module(text, render_module(path, page))
    text = rewrite_hero_image(text, path)
    text = rewrite_hero_campaign(text, page)
    text = ensure_priority_image_attrs(text)
    file.write_text(text, encoding="utf-8")


def update_methodology():
    file = ROOT / "methodology.html"
    text = file.read_text(encoding="utf-8")
    text = strip_old_schema(text)
    text = inject_schema(text, methodology_schema())
    if "data-seo-facts" not in text:
        text = text.replace("</main>", f"\n    <section class=\"section-strip\" data-seo-methodology-facts>\n      <div class=\"shell narrow-shell\">\n        <div class=\"section-head section-head-center\"><div class=\"kicker\">Product facts</div><h2>OneGLP tracking boundaries</h2></div>\n{facts_table()}\n      </div>\n    </section>\n</main>", 1)
    file.write_text(text, encoding="utf-8")


def update_home_schema():
    file = ROOT / "index.html"
    text = file.read_text(encoding="utf-8")
    text = re.sub(
        r'\n\s*<script type="application/ld\+json" data-home-schema="true">.*?</script>',
        "",
        text,
        flags=re.S | re.I,
    )
    graph = {
        "@context": "https://schema.org",
        "@graph": [
            {"@type": PUBLISHER_TYPE, "@id": f"{SITE}/#publisher", "name": PUBLISHER, "url": f"{SITE}/"},
            {"@type": "WebSite", "@id": f"{SITE}/#website", "name": "OneGLP", "url": f"{SITE}/"},
            {
                "@type": "SoftwareApplication",
                "@id": f"{SITE}/#software",
                "name": "OneGLP",
                "alternateName": REBRAND['previous_name'],
                "subjectOf": {"@id": f"{SITE}/{REBRAND_PAGE['slug']}/#webpage"},
                "applicationCategory": "HealthApplication",
                "operatingSystem": "iOS",
                "url": f"{SITE}/",
                "downloadUrl": APP_STORE,
                "description": SCHEMA_DESCRIPTION,
                "publisher": {"@id": f"{SITE}/#publisher"},
                "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"},
            },
            {"@type": "WebPage", "@id": f"{SITE}/#webpage", "url": f"{SITE}/", "name": "Private GLP-1 dose, weight and symptom tracker | OneGLP", "isPartOf": {"@id": f"{SITE}/#website"}, "author": {"@id": f"{SITE}/#publisher"}, "publisher": {"@id": f"{SITE}/#publisher"}, "dateModified": REVIEWED_ISO},
        ],
    }
    schema = '<script type="application/ld+json" data-home-schema="true">\n' + json.dumps(graph, indent=2) + "\n  </script>"
    text = inject_schema(text, schema)
    file.write_text(text, encoding="utf-8")


def main():
    for path, page in PAGES.items():
        update_priority_page(path, page)
    update_methodology()
    update_home_schema()
    print(f"updated {len(PAGES)} priority pages, methodology and homepage schema")


if __name__ == "__main__":
    main()
