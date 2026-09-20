# Website Constraints

- Prioritise search discovery, clear same-app identity and App Store downloads. Make important facts visible in static HTML, not only JavaScript or structured data. Do not claim guaranteed rankings, ChatGPT inclusion or model training.
- Keep all published translations indexable, even when wording needs improvement. Do not add translation-based `noindex` rules, remove translated URLs from the sitemap or gate hreflang on native review. Report and fix copy problems separately.
- Use root English canonicals for duplicate `/en/` URLs. Other translations keep their own canonical URLs.
- Rebuild the sitemap and reciprocal language links with `python3 tools/seo_gate_sitemap.py`. Verify with `python3 tools/locale_indexing_qa.py`.
- Commit, push or deploy only when explicitly requested. The owner approved this website rebrand release on 20 September 2026; App Store metadata changes still require separate permission.
- Preserve the existing hero design and screenshot assets pending the owner's decision.
- Steven Good is the publisher. OneGLP is the product name, previously GLPzy. Do not describe GLPzy as a legal entity or put a public "Person" label before the publisher's name.
