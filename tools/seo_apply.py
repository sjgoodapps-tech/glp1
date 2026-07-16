#!/usr/bin/env python3
import json
import re
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = "https://www.glpzy.app"
APP_STORE = "https://apps.apple.com/us/app/glpzy-glp-1-tracker/id6761775005"

PRODUCT_FACTS = {
    "app_name": "GLPzy",
    "platform": "iPhone and iPad",
    "category": "Private GLP-1 tracking app",
    "tracks": "Doses, dose reminders, injection sites, weight, symptoms, appetite, nutrition, notes, progress photos and optional read-only Apple Health context",
    "account": "No mandatory in-app account for core tracking",
    "privacy": "Local-first. Records stay on the device unless the user exports, shares or restores a local backup.",
    "apple_health": "Optional and read-only. GLPzy does not write data back to Apple Health.",
    "exports": "CSV and JSON for core records. Premium adds deeper summaries and clinician-ready PDF summaries.",
    "free_photo_allowance": "Free includes 2 new photo uploads per month. Existing photos remain available to view, compare, save and share.",
    "medical": "Personal tracking only. Not medical advice, not a dosing guide and not a medical device.",
    "app_store": APP_STORE,
}

COMMON_LINKS = [
    ("GLP-1 tracker app", "glp1-weight-dose-symptom-tracker.html"),
    ("Mounjaro tracker", "mounjaro-tracker-iphone.html"),
    ("Wegovy tracker", "wegovy-tracker-iphone.html"),
    ("Zepbound tracker", "zepbound-tracker-iphone.html"),
    ("Tirzepatide tracker", "tirzepatide-tracker-iphone.html"),
    ("Semaglutide tracker", "semaglutide-tracker-iphone.html"),
    ("Dose reminders", "glp1-dose-reminder-app.html"),
    ("Symptom tracking", "glp1-side-effect-symptom-tracker.html"),
    ("Weight tracking", "glp1-weight-tracker.html"),
    ("Progress photos", "glp1-progress-photo-tracker.html"),
    ("Apple Health", "apple-health-glp-tracker.html"),
    ("Privacy and no account", "local-first-private-glp-tracker.html"),
    ("Privacy policy", "privacy.html"),
    ("Medical safety", "medical-safety.html"),
    ("Methodology", "methodology.html"),
]

PAGES = {
    "glp1-weight-dose-symptom-tracker.html": {
        "family": "category",
        "title": "GLP-1 tracker app for iPhone | GLPzy",
        "description": "Track GLP-1 doses, reminders, weight, symptoms, appetite, nutrition, photos and optional read-only Apple Health context privately on iPhone.",
        "name": "GLP-1 tracker app for iPhone",
        "h1": "GLP-1 tracker app for iPhone",
        "campaign": "seoGlp1Tracker",
        "answer": "GLPzy is a private GLP-1 tracker for iPhone and iPad. It helps you record doses, reminders, injection sites, weight, symptoms, appetite, nutrition, notes, progress photos and optional read-only Apple Health context. It does not give medical advice, dosing advice or treatment recommendations.",
        "intro": [
            "Use this page as the main guide to what GLPzy tracks and what it does not do. GLPzy is built for personal record keeping and review, not for changing treatment.",
            "Supported contexts include Mounjaro, Wegovy, Zepbound, tirzepatide, semaglutide and other GLP-1 routines where the user wants a private tracking record."
        ],
        "screens": [("assets/en-screen-dashboard.png", "GLPzy Today dashboard showing dose, weight and quick log tools."), ("assets/en-screen-advanced-graphs.png", "GLPzy graph screen showing weight and tracking history.")],
        "faq": [
            ("What can I track in GLPzy?", "You can track doses, reminders, injection sites, weight, symptoms, appetite, nutrition, notes, progress photos and optional read-only Apple Health context."),
            ("Does GLPzy tell me how much medicine to take?", "No. GLPzy is a tracking app. It does not provide dosing advice, prescribing advice or treatment instructions."),
            ("Do I need an account?", "No. Core tracking does not require a mandatory in-app account."),
            ("Can I use GLPzy with Mounjaro, Wegovy or Zepbound?", "Yes. GLPzy can be used to keep personal records for those medicine contexts, with separate pages for each one."),
            ("Does GLPzy use Apple Health?", "Apple Health support is optional and read-only. GLPzy does not write data back to Apple Health."),
            ("Can I export my records?", "Core records can be exported as CSV and JSON. Premium adds deeper summaries and clinician-ready PDF summaries.")
        ],
    },
    "mounjaro-tracker-iphone.html": {
        "family": "medicine",
        "title": "Mounjaro tracker app for iPhone | GLPzy",
        "description": "Track Mounjaro doses, reminders, injection sites, weight, symptoms, photos and optional read-only Apple Health context privately on iPhone.",
        "name": "Mounjaro tracker app for iPhone",
        "h1": "Mounjaro tracker app for iPhone",
        "campaign": "seoMounjaro",
        "answer": "GLPzy helps you keep a private Mounjaro tracking record on iPhone. You can log dose dates, reminder times, injection sites, weight, symptoms, notes, progress photos and optional read-only Apple Health context. GLPzy is independent and does not give dosing advice.",
        "intro": [
            "Mounjaro is a brand name for tirzepatide. GLPzy is not affiliated with or endorsed by the medicine manufacturer.",
            "Use GLPzy to keep your own record for appointments, habit review and export. Always follow your clinician, pharmacist and official product information."
        ],
        "screens": [("assets/en-screen-dashboard.png", "GLPzy Today dashboard with next dose and quick log actions."), ("assets/en-screen-photos-export.png", "GLPzy photo comparison and export screen.")],
        "faq": [
            ("Can I use GLPzy as a Mounjaro tracker?", "Yes. GLPzy can track Mounjaro dose records, reminders, sites, symptoms, weight, notes and photos for personal review."),
            ("Does GLPzy give Mounjaro dosing advice?", "No. GLPzy does not provide dosing advice or treatment instructions."),
            ("Can I track side-effect notes?", "Yes. You can record symptom and side-effect notes for your own record."),
            ("Can I connect Apple Health?", "Yes. Apple Health support is optional and read-only."),
            ("Can I export records for an appointment?", "Yes. Core records can be exported as CSV and JSON, and Premium adds clinician-ready PDF summaries.")
        ],
    },
    "wegovy-tracker-iphone.html": {
        "family": "medicine",
        "title": "Wegovy tracker app for iPhone | GLPzy",
        "description": "Track Wegovy doses, reminders, weight, symptoms, photos and optional read-only Apple Health context privately on iPhone.",
        "name": "Wegovy tracker app for iPhone",
        "h1": "Wegovy tracker app for iPhone",
        "campaign": "seoWegovy",
        "answer": "GLPzy helps you track Wegovy routines privately on iPhone. You can log dose dates, reminders, injection sites, weight, symptoms, appetite, notes, progress photos and optional read-only Apple Health context. GLPzy is for personal review and does not tell you how to dose.",
        "intro": [
            "Wegovy is a brand name for semaglutide. GLPzy is not affiliated with or endorsed by the medicine manufacturer.",
            "Use GLPzy to keep weight, dose, symptom and photo records together so you can review your own history without scattered notes."
        ],
        "screens": [("assets/en-screen-projections.png", "GLPzy graph screen showing personal trend review."), ("assets/en-screen-photos-export.png", "GLPzy photo comparison and export tools.")],
        "faq": [
            ("Can I use GLPzy as a Wegovy tracker?", "Yes. GLPzy can track Wegovy dose records, reminders, weight, symptoms and photos for personal review."),
            ("Does GLPzy provide Wegovy dosing advice?", "No. GLPzy is not a dosing guide and does not provide treatment instructions."),
            ("Can I track weight beside doses?", "Yes. Weight records can be reviewed beside dose history and other context."),
            ("Can I use Apple Health weight data?", "Yes. Apple Health support is optional and read-only where you grant permission."),
            ("Can I export my Wegovy tracking history?", "Yes. Core records can be exported as CSV and JSON, and Premium adds clinician-ready PDF summaries.")
        ],
    },
    "zepbound-tracker-iphone.html": {
        "family": "medicine",
        "title": "Zepbound tracker app for iPhone | GLPzy",
        "description": "Track Zepbound doses, reminders, injection sites, weight, symptoms, photos and optional read-only Apple Health context privately on iPhone.",
        "name": "Zepbound tracker app for iPhone",
        "h1": "Zepbound tracker app for iPhone",
        "campaign": "seoZepbound",
        "answer": "GLPzy helps you keep a private Zepbound tracking record on iPhone. You can log dose dates, reminders, injection sites, weight, symptoms, notes, progress photos and optional read-only Apple Health context. GLPzy is independent and does not provide dosing advice.",
        "intro": [
            "Zepbound is a brand name for tirzepatide. GLPzy is not affiliated with or endorsed by the medicine manufacturer.",
            "Use GLPzy for your own records and appointment preparation. It does not replace clinician instructions or official product information."
        ],
        "screens": [("assets/en-screen-dashboard.png", "GLPzy Today dashboard with routine tracking cards."), ("assets/en-screen-global-coverage.png", "GLPzy setup and medicine coverage screen.")],
        "faq": [
            ("Can I use GLPzy as a Zepbound tracker?", "Yes. GLPzy can track Zepbound dose records, reminders, sites, symptoms, weight, notes and photos for personal review."),
            ("Does GLPzy provide Zepbound dosing advice?", "No. GLPzy does not provide dosing advice or treatment instructions."),
            ("Can I track injection sites?", "Yes. You can log injection sites beside dose dates and notes."),
            ("Can I review progress photos?", "Yes. Progress photo tools help you review your own visual history."),
            ("Can I export records?", "Yes. Core records can be exported as CSV and JSON, and Premium adds clinician-ready PDF summaries.")
        ],
    },
    "tirzepatide-tracker-iphone.html": {
        "family": "medicine",
        "title": "Tirzepatide tracker app for iPhone | GLPzy",
        "description": "Track tirzepatide dose records, reminders, weight, symptoms, photos and optional read-only Apple Health context privately on iPhone.",
        "name": "Tirzepatide tracker app for iPhone",
        "h1": "Tirzepatide tracker app for iPhone",
        "campaign": "seoTirzepatide",
        "answer": "GLPzy is a private tirzepatide tracker for iPhone and iPad. It can record dose dates, reminder times, injection sites, weight, symptoms, notes, photos and optional read-only Apple Health context. It is for personal review only and does not guide dosing.",
        "intro": [
            "Tirzepatide is the ingredient used in some GLP-1 and GIP medicine contexts. GLPzy supports personal tracking records without making treatment claims.",
            "Use the app to review your own routine, not to decide whether to start, stop, skip, delay or change a dose."
        ],
        "screens": [("assets/en-screen-medication-coverage.png", "GLPzy medicine setup screen."), ("assets/en-screen-advanced-graphs.png", "GLPzy trend graph screen.")],
        "faq": [
            ("Can I track tirzepatide in GLPzy?", "Yes. GLPzy can keep dose, reminder, site, weight, symptom, note and photo records for personal review."),
            ("Does GLPzy support Mounjaro and Zepbound contexts?", "Yes. GLPzy has separate pages for Mounjaro and Zepbound tracking contexts."),
            ("Does GLPzy provide dosing advice?", "No. GLPzy is not a dosing guide and does not provide treatment instructions."),
            ("What exports are available?", "Core records can be exported as CSV and JSON, and Premium adds clinician-ready PDF summaries."),
            ("Is Apple Health required?", "No. Apple Health is optional and read-only.")
        ],
    },
    "semaglutide-tracker-iphone.html": {
        "family": "medicine",
        "title": "Semaglutide tracker app for iPhone | GLPzy",
        "description": "Track semaglutide dose records, reminders, weight, symptoms, photos and optional read-only Apple Health context privately on iPhone.",
        "name": "Semaglutide tracker app for iPhone",
        "h1": "Semaglutide tracker app for iPhone",
        "campaign": "seoSemaglutide",
        "answer": "GLPzy is a private semaglutide tracker for iPhone and iPad. It can record dose dates, reminders, injection sites, weight, symptoms, appetite, notes, photos and optional read-only Apple Health context. It is for personal review only and does not guide dosing.",
        "intro": [
            "Semaglutide is used in several medicine contexts. GLPzy supports private tracking records without making treatment or availability claims.",
            "Use GLPzy to keep routine records together and export your own history when needed."
        ],
        "screens": [("assets/en-screen-advanced-graphs.png", "GLPzy graph screen for weight and routine review."), ("assets/en-screen-dashboard.png", "GLPzy Today dashboard with dose and tracking cards.")],
        "faq": [
            ("Can I track semaglutide in GLPzy?", "Yes. GLPzy can track semaglutide dose records, reminders, weight, symptoms, notes and photos."),
            ("Does GLPzy support Wegovy context?", "Yes. GLPzy has a separate Wegovy tracker page for that brand context."),
            ("Does GLPzy provide dosing advice?", "No. GLPzy is a personal tracking app, not a dosing guide."),
            ("Can I use Apple Health?", "Yes. Apple Health support is optional and read-only."),
            ("Can I export records?", "Yes. Core records can be exported as CSV and JSON, and Premium adds clinician-ready PDF summaries.")
        ],
    },
    "local-first-private-glp-tracker.html": {
        "family": "privacy",
        "title": "Private GLP-1 tracker with no account required | GLPzy",
        "description": "Use GLPzy as a private local-first GLP-1 tracker with no mandatory in-app account, on-device records, exports, local backups and optional read-only Apple Health.",
        "name": "Private GLP-1 tracker with no account required",
        "h1": "Private GLP-1 tracker with no account required",
        "campaign": "siteDefault",
        "answer": "GLPzy is a local-first GLP-1 tracker. Core tracking works without a mandatory in-app account. Your records are kept on your device unless you export, share or restore a local backup. Optional Apple Health support is read-only and does not write data back.",
        "intro": [
            "You do not need to create an in-app account to record doses, weight, symptoms, reminders or photos.",
            "Exports and local backups are user-directed. That means you choose when to create a file, share it or restore it."
        ],
        "screens": [("assets/en-screen-quick-logging.png", "GLPzy quick logging screen."), ("assets/screen-import.png", "GLPzy import and setup screen.")],
        "faq": [
            ("Do I need an account to use GLPzy?", "No. Core tracking does not require a mandatory in-app account."),
            ("Where are my records kept?", "GLPzy is local-first, so records are kept on the device unless you export, share or restore a local backup."),
            ("Does Apple Health change that?", "No. Apple Health support is optional and read-only."),
            ("What data is not required?", "Core tracking does not require a mandatory account, social login or public profile."),
            ("Can I export my records?", "Yes. Core records can be exported as CSV and JSON.")
        ],
    },
    "glp1-dose-reminder-app.html": {
        "family": "feature",
        "title": "GLP-1 dose reminder app for iPhone | GLPzy",
        "description": "Track GLP-1 dose dates, next dose reminders, last dose history, injection sites, weight, symptoms and notes privately on iPhone.",
        "name": "GLP-1 dose reminder app",
        "h1": "GLP-1 dose reminder app for iPhone",
        "campaign": "seoDoseReminder",
        "answer": "GLPzy helps you keep GLP-1 dose dates, reminder times, last dose history, injection sites and notes in one private iPhone app. It can support your routine record, but it does not change your schedule or tell you when to dose.",
        "intro": ["Use reminder records to reduce scattered calendar notes and screenshots.", "Reminder and supply views are for personal planning only, not dose instructions."],
        "screens": [("assets/en-screen-dashboard.png", "GLPzy Today dashboard with next dose timing."), ("assets/screen-recap.png", "GLPzy recap screen with recent activity.")],
        "faq": [
            ("Can GLPzy remind me about a dose?", "GLPzy can help track reminder times and next dose context for personal routine tracking."),
            ("Can I review the last dose?", "Yes. You can review last dose history, sites and notes."),
            ("Does GLPzy change my dose schedule?", "No. GLPzy does not provide dosing advice or schedule changes."),
            ("Can I track injection sites?", "Yes. Injection site records can sit beside dose records."),
            ("Is this available without an account?", "Yes. Core tracking does not require a mandatory in-app account.")
        ],
    },
    "glp1-side-effect-symptom-tracker.html": {
        "family": "feature",
        "title": "GLP-1 side effect and symptom tracker app | GLPzy",
        "description": "Track GLP-1 symptoms, side-effect notes, doses, weight, appetite, nutrition and progress photos privately on iPhone with GLPzy.",
        "name": "GLP-1 side effect and symptom tracker",
        "h1": "GLP-1 side effect and symptom tracker",
        "campaign": "seoSideEffectTracker",
        "answer": "GLPzy lets you record GLP-1 symptoms and side-effect notes beside doses, weight, appetite, nutrition and photos. It gives you a private record for review. It does not diagnose symptoms, explain side effects or provide medical advice.",
        "intro": ["Symptom tracking works best when it is plain and consistent. GLPzy keeps notes close to the dose and weight history you already record.", "If you have symptoms or safety concerns, contact a qualified healthcare professional."],
        "screens": [("assets/en-screen-dashboard.png", "GLPzy Today dashboard with quick log tools."), ("assets/en-screen-advanced-graphs.png", "GLPzy graph screen with review context.")],
        "faq": [
            ("Can I track GLP-1 symptoms in GLPzy?", "Yes. You can record symptom and side-effect notes for personal review."),
            ("Does GLPzy tell me what symptoms mean?", "No. GLPzy does not diagnose or interpret symptoms."),
            ("Can I export symptom records?", "Core records can be exported as CSV and JSON."),
            ("Can I review symptoms with weight?", "Yes. Symptoms can be reviewed beside weight and other records."),
            ("Is GLPzy medical advice?", "No. GLPzy is for personal tracking only.")
        ],
    },
    "glp1-weight-tracker.html": {
        "family": "feature",
        "title": "GLP-1 weight tracker app for iPhone | GLPzy",
        "description": "Track GLP-1 weight history, dose records, symptoms, photos and optional read-only Apple Health context privately on iPhone.",
        "name": "GLP-1 weight tracker app",
        "h1": "GLP-1 weight tracker app for iPhone",
        "campaign": "seoWeightTracker",
        "answer": "GLPzy helps you track weight history beside GLP-1 dose records, symptoms, appetite, nutrition and progress photos. Optional Apple Health support can add read-only weight context. GLPzy is for personal review and does not judge progress or give treatment advice.",
        "intro": ["Weight records are easier to understand when they sit beside dose dates, routine notes and photos.", "GLPzy can use manual entries and optional read-only Apple Health context where you grant permission."],
        "screens": [("assets/en-screen-advanced-graphs.png", "GLPzy graph screen for weight review."), ("assets/en-screen-dashboard.png", "GLPzy Today dashboard with weight card.")],
        "faq": [
            ("Can I track weight in GLPzy?", "Yes. You can track weight history beside dose and symptom records."),
            ("Can Apple Health add weight data?", "Yes. Apple Health support is optional and read-only."),
            ("Does GLPzy judge my progress?", "No. GLPzy records and shows your data for personal review."),
            ("Can I export weight records?", "Core records can be exported as CSV and JSON."),
            ("Can I review weight with photos?", "Yes. Weight and photo history can be reviewed together.")
        ],
    },
    "glp1-progress-photo-tracker.html": {
        "family": "feature",
        "title": "GLP-1 progress photo tracker app | GLPzy",
        "description": "Track GLP-1 progress photos, weight, doses, symptoms and milestones privately on iPhone with GLPzy photo comparison tools.",
        "name": "GLP-1 progress photo tracker",
        "h1": "GLP-1 progress photo tracker",
        "campaign": "seoPhotoTracker",
        "answer": "GLPzy lets you keep GLP-1 progress photos beside dose history, weight records, symptoms and notes. Free includes 2 new photo uploads per month, while Premium includes unlimited photo uploads. Photo comparison is for personal review only. It does not assess health, diagnose changes or provide medical advice.",
        "intro": ["Progress photos can help you review visible changes alongside routine records.", "GLPzy keeps photo review tied to the same private tracking history as dose, weight and symptom logs."],
        "screens": [("assets/en-screen-photos-export.png", "GLPzy progress photo comparison screen."), ("assets/en-screen-dashboard.png", "GLPzy Today dashboard with tracking context.")],
        "faq": [
            ("Can I track progress photos in GLPzy?", "Yes. GLPzy includes progress photo tracking and comparison tools."),
            ("How many progress photos can I upload for free?", "Free includes 2 new photo uploads per month. Existing photos remain available to view, compare, save and share. Premium includes unlimited photo uploads."),
            ("Can I review photos beside weight?", "Yes. Photos can be reviewed with weight and dose records."),
            ("Does GLPzy assess my photos?", "No. Photos are for personal review only."),
            ("Can I export records?", "Core records can be exported as CSV and JSON."),
            ("Do I need an account?", "No. Core tracking does not require a mandatory in-app account.")
        ],
    },
    "apple-health-glp-tracker.html": {
        "family": "feature",
        "title": "Apple Health GLP-1 tracker support | GLPzy",
        "description": "Use GLPzy with optional read-only Apple Health data for weight, height, glucose, body, movement, workouts and nutrition context on iPhone.",
        "name": "Apple Health GLP-1 tracker support",
        "h1": "Apple Health GLP-1 tracker support",
        "campaign": "seoAppleHealthInjection",
        "answer": "GLPzy can use optional read-only Apple Health context for GLP-1 tracking. With permission, it can read weight, height, glucose, body composition, movement, workouts and nutrition context. GLPzy does not write data back to Apple Health.",
        "intro": ["Apple Health is optional. Manual tracking remains the main record in GLPzy.", "Read-only Health context can help you review dose, weight, symptom and nutrition records together."],
        "screens": [("assets/en-screen-dashboard.png", "GLPzy dashboard with Apple Health context."), ("assets/screen-settings.png", "GLPzy Health and Integrations settings screen.")],
        "faq": [
            ("Is Apple Health required?", "No. Apple Health is optional."),
            ("Is Apple Health read-only?", "Yes. GLPzy reads permitted Apple Health context and does not write data back."),
            ("What Apple Health data can be used?", "With permission, GLPzy can use weight, height, glucose, body composition, movement, workout and nutrition context."),
            ("Can I disconnect Apple Health?", "Apple Health permissions can be changed in iOS settings."),
            ("Does Apple Health change medical safety?", "No. GLPzy remains a personal tracking app and not medical advice.")
        ],
    },
}


def facts_table():
    rows = [
        ("App name", PRODUCT_FACTS["app_name"]),
        ("Platform", PRODUCT_FACTS["platform"]),
        ("Category", PRODUCT_FACTS["category"]),
        ("Tracks", PRODUCT_FACTS["tracks"]),
        ("Account requirement", PRODUCT_FACTS["account"]),
        ("Privacy posture", PRODUCT_FACTS["privacy"]),
        ("Apple Health scope", PRODUCT_FACTS["apple_health"]),
        ("Export formats", PRODUCT_FACTS["exports"]),
        ("Medical boundary", PRODUCT_FACTS["medical"]),
        ("App Store link", "GLPzy on the App Store"),
    ]
    rendered_rows = []
    for k, v in rows:
        if k == "App Store link":
            value = f'<a data-app-store-link href="{APP_STORE}">{escape(v)}</a>'
        else:
            value = escape(v)
        rendered_rows.append(f'              <tr><th scope="row">{escape(k)}</th><td>{value}</td></tr>')
    body = "\n".join(rendered_rows)
    return f"""          <table class="seo-facts-table" data-seo-facts>
            <tbody>
{body}
            </tbody>
          </table>"""


def cta(campaign, label="Get GLPzy"):
    return (
        f'<a class="button button-primary" data-app-store-link '
        f'data-app-store-style="text" data-app-store-campaign="{campaign}" '
        f'href="{APP_STORE}">{label}</a>'
    )


def render_module(page):
    screen_html = "\n".join(
        f"""          <figure class="feature-card seo-screenshot">
            <img src="{src}" alt="{escape(alt)}">
            <figcaption>{escape(alt)}</figcaption>
          </figure>"""
        for src, alt in page["screens"]
    )
    faq_html = "\n".join(
        f'          <details><summary>{escape(q)}</summary><p>{escape(a)}</p></details>'
        for q, a in page["faq"]
    )
    link_html = "\n".join(
        f'          <a href="{href}">{escape(label)}</a>' for label, href in COMMON_LINKS
    )
    intro_html = "\n".join(f"          <p>{escape(p)}</p>" for p in page["intro"])
    return f"""
    <section class="section-strip seo-answer-strip" data-seo-module>
      <div class="shell narrow-shell">
        <div class="section-head section-head-center">
          <div class="kicker">Quick answer</div>
          <h2>{escape(page["name"])}</h2>
        </div>
        <div class="card seo-answer-card" data-seo-answer>
          <p>{escape(page["answer"])}</p>
          <div class="site-cta-actions">{cta(page["campaign"], "Get GLPzy")}</div>
        </div>
        <div class="seo-copy">
{intro_html}
          <p><strong>What GLPzy does not do:</strong> GLPzy does not prescribe medicine, recommend doses, diagnose symptoms, change treatment plans, replace official medicine information or replace advice from a qualified clinician.</p>
          <p data-seo-safety><strong>Safety boundary:</strong> <a href="methodology.html">Estimated Exposure</a> is a personal tracking estimate, not measured blood concentration and not medical advice. Do not use Estimated Exposure to guide dosing. Always check with your clinician before making medical decisions.</p>
        </div>
{facts_table()}
        <div class="landing-grid seo-screenshot-grid" data-seo-screenshots>
{screen_html}
        </div>
        <div class="section-head section-head-center">
          <div class="kicker">FAQ</div>
          <h2>Common questions</h2>
        </div>
        <div class="faq-mini" data-seo-faq>
{faq_html}
        </div>
        <div class="meta-links" data-seo-related>
{link_html}
        </div>
        <div class="site-cta-actions seo-bottom-cta">{cta(page["campaign"], "Get GLPzy on the App Store")}</div>
      </div>
    </section>
"""


def schema_graph(path, page):
    url = f"{SITE}/{path}"
    graph = [
        {
            "@type": "Organization",
            "@id": f"{SITE}/#organization",
            "name": "GLPzy",
            "url": f"{SITE}/",
            "logo": f"{SITE}/assets/apple-touch-icon.png",
        },
        {
            "@type": "SoftwareApplication",
            "@id": f"{SITE}/#software",
            "name": "GLPzy",
            "applicationCategory": "HealthApplication",
            "operatingSystem": "iOS",
            "url": f"{SITE}/",
            "downloadUrl": APP_STORE,
            "description": PRODUCT_FACTS["medical"],
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
        },
        {
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{SITE}/"},
                {"@type": "ListItem", "position": 2, "name": page["name"], "item": url},
            ],
        },
        {
            "@type": "FAQPage",
            "mainEntity": [
                {
                    "@type": "Question",
                    "name": q,
                    "acceptedAnswer": {"@type": "Answer", "text": a},
                }
                for q, a in page["faq"]
            ],
        },
    ]
    for src, alt in page["screens"]:
        graph.append({"@type": "ImageObject", "url": f"{SITE}/{src}", "caption": alt})
    if path == "index.html":
        graph.insert(1, {"@type": "WebSite", "@id": f"{SITE}/#website", "name": "GLPzy", "url": f"{SITE}/"})
    return '<script type="application/ld+json" data-seo-schema="true">\n' + json.dumps({"@context": "https://schema.org", "@graph": graph}, indent=2) + "\n  </script>"


def update_meta(text, page, path):
    url = f"{SITE}/{path}"
    replacements = [
        (r"<title>.*?</title>", f"<title>{escape(page['title'])}</title>"),
        (r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{escape(page["description"])}">'),
        (r'<meta property="og:title" content="[^"]*">', f'<meta property="og:title" content="{escape(page["title"])}">'),
        (r'<meta property="og:description" content="[^"]*">', f'<meta property="og:description" content="{escape(page["description"])}">'),
        (r'<meta property="og:url" content="[^"]*">', f'<meta property="og:url" content="{url}">'),
        (r'<meta name="twitter:title" content="[^"]*">', f'<meta name="twitter:title" content="{escape(page["title"])}">'),
        (r'<meta name="twitter:description" content="[^"]*">', f'<meta name="twitter:description" content="{escape(page["description"])}">'),
    ]
    for pattern, repl in replacements:
        text = re.sub(pattern, repl, text, count=1, flags=re.S)
    text = re.sub(r"(<h1[^>]*>).*?(</h1>)", r"\1" + escape(page["h1"]) + r"\2", text, count=1, flags=re.S)
    return text


def update_page(path, page):
    full = ROOT / path
    text = full.read_text(encoding="utf-8")
    text = update_meta(text, page, path)
    text = re.sub(r'\n\s*<script type="application/ld\+json"(?![^>]*data-seo-schema)[^>]*>.*?</script>', "", text, flags=re.S)
    schema = schema_graph(path, page)
    text = text.replace('  <script defer src="site-config.js"></script>', f"  {schema}\n  <script defer src=\"site-config.js\"></script>", 1)
    module = render_module(page)
    if 'data-seo-module' in text:
        text = re.sub(r'\n\s*<section class="section-strip seo-answer-strip" data-seo-module>.*?</section>\n\s*<section class="section-strip faq-strip">', "\n" + module + "    <section class=\"section-strip faq-strip\">", text, count=1, flags=re.S)
    else:
        text = text.replace('    <section class="section-strip faq-strip">', module + '    <section class="section-strip faq-strip">', 1)
    full.write_text(text, encoding="utf-8")


def main():
    for path, page in PAGES.items():
        update_page(path, page)
    print(f"updated {len(PAGES)} priority pages")


if __name__ == "__main__":
    main()
