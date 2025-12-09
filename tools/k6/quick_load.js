import http from 'k6/http';
import { sleep, check } from 'k6';

export const options = {
  stages: [
    { duration: '1m', target: 100 },
    { duration: '1m', target: 100 },
    { duration: '30s', target: 0 },
  ],
};

const BASE = __ENV.BASE_URL || 'http://127.0.0.1:8085/api/v1';
const TOKEN = __ENV.TOKEN;

export default function () {
  const buf = new ArrayBuffer(1024 * 1024 * 5); // 5MB
  const fd = { file: http.file(buf, 'quick.bin', 'application/octet-stream') };
  const res = http.post(`${BASE}/files/upload`, fd, { headers: { Authorization: `Bearer ${TOKEN}` } });
  check(res, { 'status 200': (r) => r.status === 200 });
  sleep(1);
}
