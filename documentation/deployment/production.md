# Production / Remote Deployment

## Goals
- Run beyond localhost; accessible from other devices or the internet.

## Steps (Single Host)
1. Assign a static LAN IP or domain to the host.
2. Put API behind a reverse proxy (Nginx/Traefik) with TLS.
3. Set `VITE_API_URL` of both frontends to `https://<domain-or-ip>/api/v1`.
4. Harden CORS in FastAPI to allow only your frontend origins.
5. Open firewall ports: 80/443 (frontends + API via proxy). Keep node gRPC internal.
6. Persist Postgres volume and configure backups.

## Compose Overrides
- Create `docker-compose.prod.yml` to override env vars and add reverse proxy.
- Example Nginx location:
```
location /api/ {
  proxy_pass http://storage_service:8085/;
  proxy_set_header Host $host;
  proxy_set_header X-Forwarded-Proto $scheme;
}
```

## Multi-Device Access (LAN)
- Use the host IP in browsers on other devices: `http://<host-ip>:5175`.
- Update frontends `VITE_API_URL` to `http://<host-ip>:8085/api/v1`.

## Secrets
- Replace dev secrets (SECRET_KEY) and store in a secrets manager.
