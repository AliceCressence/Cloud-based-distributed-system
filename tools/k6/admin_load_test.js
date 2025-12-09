import http from 'k6/http';
import { check, sleep } from 'k6';

const BASE_URL = __ENV.BASE_URL || 'http://host.docker.internal:8085/api/v1';
const TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImVtYWlsIjoiYWRtaW5AaWN0bmV4dXMuZWR1Iiwicm9sZSI6ImFkbWluIiwiZXhwIjoxNzY1MjY5NDAwfQ.CrIZK6fAIOJWqY_lij-MA6TYIT3lRvHuwr4SygUO4Sk';

export const options = {
  vus: 10,
  duration: '30s',
  thresholds: {
    http_req_failed: ['rate<0.1'],  // <10% errors
    http_req_duration: ['p(95)<500'], // 95% of requests <500ms
  },
};

const params = {
  headers: {
    'Authorization': `Bearer ${TOKEN}`,
    'Content-Type': 'application/json',
  },
};

export default function () {
  // Test GET /nodes
  const res1 = http.get(`${BASE_URL}/nodes`, params);
  check(res1, { 'nodes status 200': (r) => r.status === 200 });
  
  // Test GET /nodes/overview
  const res2 = http.get(`${BASE_URL}/nodes/overview`, params);
  check(res2, { 'overview status 200': (r) => r.status === 200 });
  
  // Test GET /admin/stats
  const res3 = http.get(`${BASE_URL}/admin/stats`, params);
  check(res3, { 'stats status 200': (r) => r.status === 200 });
  
  sleep(1);
}
