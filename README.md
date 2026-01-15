![CI](https://github.com/BTExpress1/healthcare-cicd-phase5/actions/workflows/ci.yml/badge.svg)

# healthcare-cicd-phase5

Phase 5 of **Healthcare Signals — Provider Risk Analytics** focuses on **real CI/CD discipline**:
- deterministic validation gates
- data contracts (schema, freshness, constraints)
- snapshot regression checks (metrics + top-K stability)
- CI artifacts for auditability

## Quickstart
```bash
make setup
make ci
