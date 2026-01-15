
---

## `PRODUCTION.md`
```md
# Production Readiness Notes (Phase 5)

## Operating model
Pipeline stages:
1) Ingest / load
2) Contract validation (fail fast)
3) Risk output validation
4) Snapshot report + regression
5) Publish artifacts

## What can break (and how we catch it)
- Missing columns → contract check fails
- Type drift (dates/numbers) → parsing fails
- Duplicate keys → uniqueness check fails
- Out-of-range risk score → constraint fails
- Stale data → freshness check fails
- Behavioral drift → snapshot regression fails

## Recovery
- Fix upstream extract or mapping
- Regenerate outputs
- Update baseline snapshot only when drift is expected and reviewed
