# Email OTP Verification Feature

## Overview
New users must verify their email address using a One-Time Password (OTP) sent to their email before their account becomes fully active.

## How It Works

### 1. User Registration Flow
```
1. User enters registration details (email, password, role)
2. System sends 6-digit OTP to user's email
3. User receives OTP code (valid for 10 minutes)
4. User enters OTP code to verify email
5. Account is activated after successful verification
```

### 2. Database Schema

**users table** - Added field:
- `email_verified` (BOOLEAN) - Whether email has been verified

**email_verifications table** - New table:
- `id` - Primary key
- `email` - Email address
- `otp_code` - 6-digit OTP code
- `created_at` - When OTP was created
- `expires_at` - When OTP expires (10 minutes)
- `is_used` - Whether OTP has been used
- `verified_at` - When email was verified

### 3. API Endpoints

**Request OTP**
```http
POST /api/v1/verify/request-otp
Content-Type: application/json

{
  "email": "student@ictnexus.edu"
}
```

**Verify OTP**
```http
POST /api/v1/verify/verify-otp
Content-Type: application/json

{
  "email": "student@ictnexus.edu",
  "otp_code": "123456"
}
```

**Resend OTP**
```http
POST /api/v1/verify/resend-otp
Content-Type: application/json

{
  "email": "student@ictnexus.edu"
}
```

## Setup Instructions

### 1. Apply Database Migration
```bash
docker exec storage_db psql -U storage_user -d ictnexus_storage -f /app/database/add_email_verification.sql
```

Or manually:
```bash
cd storage-service/database
docker cp add_email_verification.sql storage_db:/tmp/
docker exec storage_db psql -U storage_user -d ictnexus_storage -f /tmp/add_email_verification.sql
```

### 2. Configure Email Settings (Production)

Add to `.env` file:
```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=noreply@ictnexus.edu
```

### 3. Enable in Main App

Update `storage-service/app/main.py`:
```python
from .routers import auth, files, nodes, admin, email_verification

app.include_router(email_verification.router, prefix="/api/v1")
```

## Development Mode

In development, OTP codes are printed to console logs instead of being sent via email:

```bash
# View OTP codes in logs
docker logs storage_service | grep "EMAIL OTP"
```

Output example:
```
[EMAIL OTP] To: student@ictnexus.edu | Code: 123456
```

## Frontend Integration

### Registration Component
```typescript
// 1. Register user
const registerUser = async (userData) => {
  const response = await api.post('/auth/register', userData);
  // After registration, request OTP
  await api.post('/verify/request-otp', { email: userData.email });
  return response.data;
};

// 2. Verify OTP
const verifyEmail = async (email, otpCode) => {
  const response = await api.post('/verify/verify-otp', {
    email,
    otp_code: otpCode
  });
  return response.data;
};

// 3. Resend OTP if needed
const resendOTP = async (email) => {
  const response = await api.post('/verify/resend-otp', { email });
  return response.data;
};
```

### UI Flow
1. **Registration Form** → Enter email, password, role
2. **OTP Sent Screen** → "Check your email for verification code"
3. **OTP Input Screen** → 6-digit code input with resend button
4. **Success Screen** → "Email verified! You can now login"

## Security Features

- ✅ OTP expires after 10 minutes
- ✅ Each OTP can only be used once
- ✅ Old OTPs are invalidated when new one is requested
- ✅ Rate limiting recommended (not yet implemented)
- ✅ Email validation before OTP generation

## Testing

### Test OTP Flow (Development)
```bash
# 1. Request OTP
curl -X POST http://localhost:8085/api/v1/verify/request-otp \
  -H "Content-Type: application/json" \
  -d '{"email":"test@ictnexus.edu"}'

# 2. Check logs for OTP code
docker logs storage_service --tail 20 | grep "EMAIL OTP"

# 3. Verify OTP
curl -X POST http://localhost:8085/api/v1/verify/verify-otp \
  -H "Content-Type: application/json" \
  -d '{"email":"test@ictnexus.edu","otp_code":"123456"}'
```

## Production Deployment

### Recommended Email Providers
- **AWS SES** (Amazon Simple Email Service)
- **SendGrid**
- **Mailgun**
- **Google Workspace SMTP**

### Environment Configuration
```bash
# AWS SES Example
SMTP_HOST=email-smtp.us-east-1.amazonaws.com
SMTP_PORT=587
SMTP_USERNAME=YOUR_AWS_ACCESS_KEY
SMTP_PASSWORD=YOUR_AWS_SECRET_KEY
SMTP_FROM_EMAIL=noreply@yourdomain.com
```

## Future Enhancements

- [ ] SMS OTP as alternative to email
- [ ] Rate limiting (max 3 OTP requests per 10 minutes)
- [ ] Email templates with HTML formatting
- [ ] Multi-language support
- [ ] OTP analytics and monitoring
- [ ] Account lockout after failed verifications

## Benefits

1. **Security**: Confirms email ownership
2. **Spam Prevention**: Reduces fake account creation  
3. **Contact Verification**: Ensures users can receive important notifications
4. **Academic Integrity**: Links storage to verified university email
5. **Compliance**: Meets data privacy requirements

---

**Status**: ✅ Feature code implemented, ready for integration  
**Created**: December 2, 2025  
**Author**: NZEKUI NZOUDJIO ALICE CRESSENCE
