# Security Testing

See root `SECURITY_TESTING_GUIDE.md` for detailed steps.

Additional checks for remote deployments:
- Verify HTTPS certificate validity and HSTS.
- Confirm CORS allow-list matches frontend domains only.
- Attempt XSS to ensure tokens are not accessible (if using cookies).
