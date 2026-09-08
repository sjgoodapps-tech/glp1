#!/usr/bin/env python3
"""Apply reviewed key-based website copy without rebuilding static templates."""
import argparse
import json
import re
from pathlib import Path

from localisation_qa import LOCALE_DIRS, locale_for
from sync_site_content import replace_data_copy

ROOT = Path(__file__).resolve().parents[1]
COPY = json.loads((ROOT / "data/website-copy.json").read_text(encoding="utf-8"))
KEYS = COPY["keys"]
assert all(len(values) == len(KEYS) for values in COPY["translations"].values())
TRANSLATIONS = {locale: dict(zip(KEYS, values)) for locale, values in COPY["translations"].items()}
ESSENTIAL = json.loads((ROOT / "data/website-essential-copy.json").read_text(encoding="utf-8"))
assert all(len(values) == len(ESSENTIAL["keys"]) for values in ESSENTIAL["translations"].values())
ESSENTIAL_TRANSLATIONS = {locale: dict(zip(ESSENTIAL["keys"], values)) for locale, values in ESSENTIAL["translations"].items()}
assert set(TRANSLATIONS) | set(ESSENTIAL_TRANSLATIONS) | {"en-gb"} == LOCALE_DIRS
CORE = json.loads((ROOT / "data/website-core-copy.json").read_text(encoding="utf-8"))
assert set(CORE['translations']) == set(ESSENTIAL_TRANSLATIONS)
CORE_TRANSLATIONS = {locale: dict(zip(CORE['keys'], values)) for locale, values in CORE['translations'].items()}
LABELS = json.loads((ROOT / 'data/website-label-copy.json').read_text(encoding='utf-8'))
assert set(LABELS['translations']) == set(ESSENTIAL_TRANSLATIONS)
LABEL_TRANSLATIONS = {locale: dict(zip(LABELS['keys'], values)) for locale, values in LABELS['translations'].items()}


def corrected_html(rel, text):
    locale = locale_for(rel)
    copy = TRANSLATIONS.get("en" if locale in {"root", "en", "en-gb"} else locale)
    # The keys are literal dotted identifiers, not paths through a JSON object.
    if copy:
        for key, value in copy.items():
            text = replace_data_copy(text, "data-i18n", nest_key(key, value))
        if locale == "ko":
            for key in ("history.export.title", "site.card.control.title"):
                text = replace_data_copy(text, "data-i18n", nest_key(key, copy["site.card.control.title"]))
    elif locale in LOCALE_DIRS:
        # Do not keep known incorrect operation/entitlement claims in lower-priority
        # locales, or fill them with English. Restore these optional cards only with
        # approved translations in website-copy.json.
        text = re.sub(r'<article\b[^>]*>(?:(?!</article>).)*data-i18n="site\.card\.premium\.(?:calendar|exports)\.[^"]+"(?:(?!</article>).)*</article>', '', text, flags=re.S)
        for key in ("site.premium.body",):
            text = re.sub(r'<(?P<tag>p|h[1-6]|span)\b[^>]*data-i18n="' + re.escape(key) + r'"[^>]*>.*?</(?P=tag)>', '', text, flags=re.S)
        for key, value in ESSENTIAL_TRANSLATIONS[locale].items():
            text = replace_data_copy(text, "data-i18n", nest_key(key, value))
        core = CORE_TRANSLATIONS[locale]
        for key in ('services.copy.no.account.is.required.to.track.doses.weight', 'site.privacy.body', 'site.card.account.title', 'site.privacy.detail.body'):
            text = replace_data_copy(text, 'data-i18n', nest_key(key, core['account']))
        for key in ('site.card.health.body', 'site.health.detail.body', 'services.copy.apple.health.access.is.optional.and.limited.to'):
            text = replace_data_copy(text, 'data-i18n', nest_key(key, core['health']))
        for key in ('site.card.log.body', 'site.product.card.log.body'):
            text = replace_data_copy(text, 'data-i18n', nest_key(key, core['records']))
        labels = LABEL_TRANSLATIONS[locale]
        label_keys = {
            'onboarding.medication.routeCadence': 'route',
            'onboarding.medication.presentation.detail': 'choose_form',
            'settings.copy.presentation': 'form',
            'site.card.provider.title': 'summary',
            'site.product.card.summary.title': 'summary',
            'site.card.provider.body': 'pdf',
            'site.product.card.summary.body': 'pdf',
            'site.card.log.title': 'dose',
            'site.product.card.log.title': 'dose',
        }
        for key, label in label_keys.items():
            text = replace_data_copy(text, 'data-i18n', nest_key(key, labels[label]))

    # Resolve the current page's English equivalent in static HTML, including when
    # scripts are disabled. Keep relative URLs working in file and HTTP previews.
    candidate = rel.split('/', 1)[1] if locale in LOCALE_DIRS else rel
    if not (ROOT / candidate).is_file():
        candidate = "index.html"
    prefix = "../" * (len(Path(rel).parts) - 1)
    def language_link(match):
        return re.sub(r'href="[^"]*"', f'href="{prefix}{candidate}"', match.group(0))
    text = re.sub(r'<a\b(?=[^>]*data-language-option="en")[^>]*>', language_link, text)
    return text


def nest_key(key, value):
    for part in reversed(key.split('.')):
        value = {part: value}
    return value


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    changes = []
    for path in sorted(ROOT.rglob('*.html')):
        if '.git' in path.parts:
            continue
        before = path.read_text(encoding='utf-8')
        after = corrected_html(path.relative_to(ROOT).as_posix(), before)
        if before != after:
            changes.append(path)
            if not args.check:
                path.write_text(after, encoding='utf-8')
    print(f'Website copy {"drift" if args.check else "updated"}: {len(changes)} pages; '
          f'{len(TRANSLATIONS) - 1} translated locales; other locales keep index gates and omit unapproved optional claims.')
    return int(args.check and bool(changes))


if __name__ == '__main__':
    raise SystemExit(main())
