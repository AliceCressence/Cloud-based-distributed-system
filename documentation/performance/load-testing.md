# Load Testing Guide

## Goals
- Understand throughput, latency, and resource usage under concurrent uploads/downloads.
- Validate node distribution and replication behavior.

## Tools
- k6 (JavaScript-based) or Locust (Python-based)
- Grafana/Prometheus (optional) for metrics

## k6 Example (Upload)
```js
import http from 'k6/http';
import { sleep, check } from 'k6';

export const options = {
  stages: [
    { duration: '2m', target: 200 },
    { duration: '5m', target: 500 },
    { duration: '10m', target: 500 },
    { duration: '2m', target: 0 },
  ],
};

const BASE = __ENV.BASE_URL || 'http://127.0.0.1:8085/api/v1';
const TOKEN = __ENV.TOKEN;

export default function () {
  const data = { file: http.file(new Uint8Array(1024*1024*5), 'test.bin', 'application/octet-stream') };
  const res = http.post(`${BASE}/files/upload`, data, {
    headers: { Authorization: `Bearer ${TOKEN}` },
  });
  check(res, { 'status is 200': (r) => r.status === 200 });
  sleep(1);
}
```

Run:
```
BASE_URL=http://<server-ip>:8085/api/v1 TOKEN=<jwt> k6 run k6-upload.js
```

## Metrics to Capture
- Success rate
- Avg/p95/p99 latency per endpoint
- Queue depth (if broker enabled)
- Node used_bytes and chunk counts (via /nodes/overview)
- DB CPU, I/O, and connection pool usage

## Reporting
- Export k6 summary (JSON) and attach to testing/results.md
- Capture `GET /api/v1/nodes/overview` before/after to show distribution
