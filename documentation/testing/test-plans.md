# Test Plans

## Functional
- Upload, list, download, delete flows per role.
- Quota enforcement and error messages.
- Node overview shows correct totals.

## Performance
- k6 concurrent uploads (200–1000 VUs) with varying file sizes.
- Record latency, throughput, node usage before/after.

## Resilience
- Kill a node: verify reads via replicas; measure impact.
- DB restart: API recovers; no data loss in metadata.

## Security
- Follow SECURITY_TESTING_GUIDE.md for content moderation and auth tests.
