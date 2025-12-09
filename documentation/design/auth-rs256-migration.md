# Auth Migration: RS256 + httpOnly Cookies

This guide outlines how to migrate from HS256 tokens in localStorage to RS256-signed tokens stored in httpOnly cookies.

## Why
- Mitigate XSS risk (tokens inaccessible to JS when using httpOnly cookies).
- Enable key rotation and better secret handling with asymmetric keys.

## Steps
1. Generate keys (example):
```
openssl genrsa -out jwtRS256.key 2048
openssl rsa -in jwtRS256.key -pubout -out jwtRS256.key.pub
```
Store privately and mount into the API container as secrets.

2. FastAPI settings
- Use RS256: set `algorithm = "RS256"`.
- Load `private_key` and `public_key` from files/ENV.
- Sign access tokens with private key; verify with public key.

3. Token delivery
- Return tokens in secure httpOnly cookies:
  - `Set-Cookie: access=...; HttpOnly; Secure; SameSite=Strict; Path=/`
  - `Set-Cookie: refresh=...; HttpOnly; Secure; SameSite=Strict; Path=/auth`
- Remove Authorization header usage on the frontend; rely on cookies.

4. CORS and Cookie Settings
- Enable `allow_credentials=True`.
- Set `allow_origins` to the exact frontend domains.
- On frontend dev, ensure requests use `withCredentials` where needed.

5. Logout and Rotation
- On logout: clear cookies and blacklist refresh token (DB or cache).
- Rotate signing keys periodically; support key IDs (kid) and JWKS endpoint.

6. Backward Compatibility
- During migration, accept both HS256 and RS256 for a short window; switch verifiers based on `alg` or `kid`.

## Example Compose Snippet (Secrets)
```
services:
  storage-service:
    environment:
      JWT_ALGORITHM: RS256
      JWT_PUBLIC_KEY_PATH: /run/secrets/jwt_pub
      JWT_PRIVATE_KEY_PATH: /run/secrets/jwt_priv
    secrets:
      - jwt_pub
      - jwt_priv
secrets:
  jwt_pub:
    file: ./secrets/jwtRS256.key.pub
  jwt_priv:
    file: ./secrets/jwtRS256.key
```

## Testing
- Verify cookies are set with HttpOnly, Secure, SameSite.
- Validate tokens with public key; revoke/rotate and ensure behavior is correct.
