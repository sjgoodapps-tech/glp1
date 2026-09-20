# Indexation and Consolidation Summary

Generated: 2026-09-20T00:43:12+00:00
Pages mapped: 1357
Native-reviewed locales: none

## Decision Counts

- `keep_index_priority`: 19
- `keep_index_supporting`: 6
- `keep_index_translation`: 1300
- `keep_root_canonical_duplicate`: 24
- `monitor_then_consolidate`: 8

## Rules

- Root English priority and trust pages remain indexable.
- `/en/` duplicates use `index,follow` and point to root English canonicals.
- All published translations remain indexable, in the sitemap and linked by hreflang. Native review is a copy-quality check, not an indexing gate.
- Overlapping root medicine pages are not merged without at least 28 days of Search Console query data.
- A consolidation target is a decision aid, not an automatic redirect instruction.
