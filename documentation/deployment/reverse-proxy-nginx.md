# Reverse Proxy (Nginx) with TLS

Use a reverse proxy to expose the API and frontends over HTTPS and to enforce security headers and CORS.

## Goals
- Single public endpoint with HTTPS
- Proxy to Storage Service API and React frontends
- Add security headers and CORS

## Example Directory Layout
```
reverse-proxy/
  nginx.conf
  certs/             # place cert/key here or use Let's Encrypt
```

## nginx.conf (Example)
```
worker_processes auto;

http {
  server {
    listen 80;
    server_name _;

    # Redirect to HTTPS (if TLS available)
    # return 301 https://$host$request_uri;

    # Optional: serve frontends directly if built to static
    # location / {
    #   root /usr/share/nginx/html/client;
    #   try_files $uri /index.html;
    # }

    location /client/ {
      proxy_pass http://storage_client_portal:5173/;
    }

    location /admin/ {
      proxy_pass http://storage_admin_portal:5173/;
    }

    location /api/ {
      proxy_pass http://storage_service:8085/;
      proxy_set_header Host $host;
      proxy_set_header X-Forwarded-Proto $scheme;

      add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload" always;
      add_header X-Content-Type-Options nosniff;
      add_header X-Frame-Options DENY;
      add_header Referrer-Policy no-referrer;
      add_header Permissions-Policy "geolocation=(), microphone=(), camera=()";
    }
  }
}
```

## Compose Override (Example)
Create `docker-compose.proxy.yml`:
```
version: "3.9"
services:
  reverse-proxy:
    image: nginx:1.27
    container_name: storage_nginx
    volumes:
      - ./reverse-proxy/nginx.conf:/etc/nginx/nginx.conf:ro
    ports:
      - "80:80"
      # - "443:443"   # enable when TLS certs configured
    depends_on:
      - storage-service
      - storage-client-portal
      - storage-admin-portal
    networks:
      - ums-net

networks:
  ums-net:
    external: true
```

Run with:
```
docker compose -f docker-compose.storage.yml -f docker-compose.proxy.yml up -d --build
```

## TLS Options
- Use a real domain and Let's Encrypt (e.g., with Traefik/Caddy for auto certificates), or
- Mount `server.crt` and `server.key` into Nginx and enable `listen 443 ssl;` with proper `ssl_certificate` directives.

## CORS Hardening (FastAPI)
- Replace `allow_origins=["*"]` with specific origins: `https://your-domain`, `http://<lan-ip>:5175`, etc.
- Keep methods/headers narrowed if possible.
