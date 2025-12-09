# Local Development

## Prerequisites
- Docker Desktop
- Node.js 18+

## Start Services
```
docker-compose -f docker-compose.storage.yml up -d --build
```
- Client Portal: http://localhost:5175
- Admin Portal: http://localhost:5176
- API: http://localhost:8085/api/v1

## Environment
- Frontends use `VITE_API_URL` (set in compose).
- API CORS is permissive for local dev; restrict in prod.
