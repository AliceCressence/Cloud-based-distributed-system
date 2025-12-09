# Performance Test Report - Admin API Endpoints
**Date**: 2025-12-09  
**Test Type**: Load Test  
**Environment**: Local Docker Setup  
**Test Duration**: 30 seconds

## Test Configuration
```javascript
export const options = {
  vus: 10,
  duration: '30s',
  thresholds: {
    http_req_failed: ['rate<0.1'],
    http_req_duration: ['p(95)<500ms']
  }
};
```

## Tested Endpoints
1. `GET /api/v1/nodes`
2. `GET /api/v1/nodes/overview`
3. `GET /api/v1/admin/stats`

## Results Summary
| Metric | Value | Threshold | Status |
|--------|-------|-----------|--------|
| Total Requests | 810 | - | ✅ |
| Requests/s | 26.12 | - | ✅ |
| Success Rate | 100% | >90% | ✅ |
| p95 Response Time | 74.8ms | <500ms | ✅ |
| Data Transferred | 547 KB | - | - |
| Iterations | 270 | - | - |

## Detailed Metrics
- **HTTP Request Duration**:
  - p(95): 74.8ms
  - p(99): 89.2ms
  - max: 131ms

- **Iteration Duration**:
  - avg: 1.12s
  - min: 1.04s
  - max: 1.31s

## System Performance
- **Virtual Users**:
  - min: 2
  - max: 10
- **Network**:
  - Data received: 547 kB (18 kB/s)
  - Data sent: 378 kB (12 kB/s)

## Observations
- System handled the load effortlessly with no errors
- Response times were consistently low
- Throughput was stable throughout the test
- All thresholds were met with significant margin

## Recommendations
1. System can handle higher loads - consider testing with more VUs
2. Monitor resource usage in future tests
3. Consider testing with larger payloads
4. Test with mixed read/write operations
