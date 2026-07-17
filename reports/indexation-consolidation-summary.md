# Indexation and Consolidation Summary

Generated: 2026-07-17T00:03:42+00:00
Pages mapped: 1304
Native-reviewed locales: none

## Decision Counts

- `keep_index_priority`: 19
- `keep_index_supporting`: 5
- `keep_noindex_duplicate`: 24
- `keep_noindex_pending_native_review`: 1248
- `monitor_then_consolidate`: 8

## Rules

- Root English priority and trust pages remain indexable.
- `/en/` duplicates remain `noindex,follow` and point to root English canonicals.
- A locale is not indexable until native approval is recorded in `data/locale-indexing.json`.
- Overlapping root medicine pages are not merged without at least 28 days of Search Console query data.
- A consolidation target is a decision aid, not an automatic redirect instruction.
