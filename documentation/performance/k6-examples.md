# k6 Examples

## Upload Test
```js
import http from 'k6/http';
import { sleep, check } from 'k6';

export const options = {
  stages: [
    { duration: '1m', target: 100 },
    { duration: '3m', target: 300 },
    { duration: '5m', target: 300 },
    { duration: '1m', target: 0 },
  ],
};

const BASE = __ENV.BASE_URL || 'http://127.0.0.1:8085/api/v1';
const TOKEN = __ENV.TOKEN;

export default function () {
  const bytes = new Uint8Array(1024 * 1024 * 5); // 5MB
  const fd = { file: http.file(bytes, 'test.bin', 'application/octet-stream') };
  const res = http.post(`${BASE}/files/upload`, fd, { headers: { Authorization: `Bearer ${TOKEN}` } });
  check(res, { 'status 200': (r) => r.status === 200 });
  sleep(1);
}
```
Run:
```
BASE_URL=http://<host>:8085/api/v1 TOKEN=<jwt> k6 run upload.js
```

## Download Test
```js
import http from 'k6/http';
import { sleep, check } from 'k6';

export const options = { vus: 100, duration: '5m' };
const BASE = __ENV.BASE_URL || 'http://127.0.0.1:8085/api/v1';
const TOKEN = __ENV.TOKEN;
const FILE_ID = __ENV.FILE_ID; // set to a valid uploaded file id

export default function () {
  const res = http.get(`${BASE}/files/${FILE_ID}/download`, { headers: { Authorization: `Bearer ${TOKEN}` } });
  check(res, { 'status 200': (r) => r.status === 200 });
  sleep(1);
}
```
Run:
```
BASE_URL=http://<host>:8085/api/v1 TOKEN=<jwt> FILE_ID=<id> k6 run download.js
```

## What to Record
- Success rate
- Avg/p95/p99 latency
- Throughput (req/s)
- Node usage before/after (`GET /api/v1/nodes/overview`)
- Any errors
