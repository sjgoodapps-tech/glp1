# Scheduled Offer Expiry Workflow QA

Tested: 17 July 2026
Method: isolated clean Git repository using the release candidate files

## Before Expiry

- Test time: `2026-08-31T22:59:59+00:00`
- Equivalent London time: `2026-08-31T23:59:59+01:00`
- Content sync result: active offer, 0 files changed
- Sitemap result: 32 URLs, 0 files changed
- Git result: clean worktree

## At Expiry

- Test time: `2026-09-01T00:00:00+01:00`
- Equivalent UTC time: `2026-08-31T23:00:00+00:00`
- Content sync result: expired offer, 14 crawler-visible pages changed
- Expired-state sync check: passed
- Sitemap result: 32 URLs
- Diff guard: passed, with only the 14 offer pages and `sitemap.xml` changed

## Workflow Safety

- The date-specific run is scheduled for 23:07 UTC on 31 August 2026.
- A daily 00:17 UTC fallback covers a delayed or missed scheduled run.
- The job has only `contents: write` permission.
- The job exits without a commit when there is no change.
- The diff guard stops the job if any file outside the approved offer pages and sitemap changes.
- The workflow can also be run manually with `workflow_dispatch`.
