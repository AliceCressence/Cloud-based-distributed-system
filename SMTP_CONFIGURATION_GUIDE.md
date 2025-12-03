# 📧 SMTP Configuration Guide for Email OTP

**Purpose**: Configure email sending for OTP verification during user signup  
**Date**: December 2, 2025

---

## 🎯 Quick Summary

**Current Status**: OTP codes are printed to backend logs (development mode)  
**To Enable Email**: Configure SMTP settings with Gmail App Password  
**Time Required**: ~5 minutes

---

## 📍 Where to Put SMTP Configuration

### **Option 1: Using .env File (Recommended for Development)**

1. **Create `.env` file** in `storage-service/` folder:
   ```
   c:\Users\noble\Downloads\dsc\Cressencia\storage-service\.env
   ```

2. **Copy from `.env.example` and update**:
   ```bash
   # Email/SMTP Configuration
   SMTP_HOST=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USERNAME=your-email@gmail.com
   SMTP_PASSWORD=your-16-digit-app-password
   SMTP_FROM_EMAIL=noreply@ictnexus.edu
   SMTP_FROM_NAME=ICTNexus Storage
   SMTP_ENABLED=true
   ```

### **Option 2: Using Docker Compose Environment Variables**

Add to `docker-compose.storage.yml` under `storage-service`:
```yaml
storage-service:
  environment:
    - SMTP_HOST=smtp.gmail.com
    - SMTP_PORT=587
    - SMTP_USERNAME=your-email@gmail.com
    - SMTP_PASSWORD=your-app-password
    - SMTP_FROM_EMAIL=noreply@ictnexus.edu
    - SMTP_FROM_NAME=ICTNexus Storage
    - SMTP_ENABLED=true
```

---

## 🔐 How to Get Gmail App Password

### **Step-by-Step Guide**:

1. **Go to Google Account**:
   ```
   https://myaccount.google.com/
   ```

2. **Enable 2-Step Verification** (if not already):
   - Go to Security → 2-Step Verification
   - Follow setup wizard

3. **Create App Password**:
   - Go to: https://myaccount.google.com/apppasswords
   - Or: Security → 2-Step Verification → App passwords
   - Select: **Mail** and **Other (Custom name)**
   - Name it: `ICTNexus Storage`
   - Click **Generate**

4. **Copy the 16-character password**:
   - Format: `xxxx xxxx xxxx xxxx`
   - Remove spaces when pasting: `xxxxxxxxxxxxxxxx`

5. **Paste into your configuration**:
   ```
   SMTP_PASSWORD=abcdefghijklmnop
   ```

---

## 🚀 Configuration Methods

### **Method 1: .env File (Local Development)**

**Step 1: Create .env file**
```powershell
cd c:\Users\noble\Downloads\dsc\Cressencia\storage-service
New-Item .env -ItemType File
```

**Step 2: Edit .env file**
```env
# Add these lines to your .env file:
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=youremail@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=noreply@ictnexus.edu
SMTP_FROM_NAME=ICTNexus Storage
SMTP_ENABLED=true
```

**Step 3: Restart backend**
```powershell
docker-compose -f docker-compose.storage.yml restart storage-service
```

---

### **Method 2: Docker Compose (Recommended)**

**Step 1: Edit docker-compose.storage.yml**
```yaml
services:
  storage-service:
    # ... existing config ...
    environment:
      - DATABASE_URL=postgresql://storage_user:storage_pass@storage-db:5432/ictnexus_storage
      # Add SMTP settings:
      - SMTP_HOST=smtp.gmail.com
      - SMTP_PORT=587
      - SMTP_USERNAME=${SMTP_USERNAME}
      - SMTP_PASSWORD=${SMTP_PASSWORD}
      - SMTP_FROM_EMAIL=noreply@ictnexus.edu
      - SMTP_FROM_NAME=ICTNexus Storage
      - SMTP_ENABLED=true
```

**Step 2: Create .env in project root**
```env
SMTP_USERNAME=youremail@gmail.com
SMTP_PASSWORD=your-app-password
```

**Step 3: Restart services**
```powershell
docker-compose -f docker-compose.storage.yml down
docker-compose -f docker-compose.storage.yml up -d
```

---

## 🧪 Testing SMTP Configuration

### **Step 1: Enable SMTP**
Make sure `SMTP_ENABLED=true` in your configuration

### **Step 2: Restart backend**
```powershell
docker-compose -f docker-compose.storage.yml restart storage-service
```

### **Step 3: Check logs to confirm settings loaded**
```powershell
docker logs storage_service | Select-String "SMTP"
```

### **Step 4: Test signup flow**
1. Go to: http://localhost:5175/signup
2. Enter test email (your real email)
3. Fill form and click "Continue to Verification"
4. **Check your email inbox** for OTP code
5. If email not received, check:
   - Spam folder
   - Backend logs: `docker logs storage_service --tail 50`

### **Step 5: Verify in logs**
```powershell
docker logs storage_service --tail 20
```

**Success looks like**:
```
[EMAIL OTP] To: test@gmail.com | Code: 123456
[EMAIL OTP] Email sent successfully to test@gmail.com
```

**Failure looks like**:
```
[EMAIL OTP] To: test@gmail.com | Code: 123456
[EMAIL OTP] SMTP Error: (535, b'5.7.8 Username and Password not accepted')
```

---

## 🔍 Troubleshooting

### **Issue: "Username and Password not accepted"**

**Solution**:
- ✅ Use **App Password**, not your regular Gmail password
- ✅ Remove spaces from app password
- ✅ Enable 2-Step Verification first
- ✅ Generate new app password

### **Issue: "SMTP connection failed"**

**Solution**:
- ✅ Check SMTP_HOST: `smtp.gmail.com`
- ✅ Check SMTP_PORT: `587`
- ✅ Ensure internet connection

### **Issue: Email not received**

**Solutions**:
1. Check spam folder
2. Verify email address is correct
3. Check backend logs for errors
4. Try different email provider
5. Check Gmail "Less secure app" settings

### **Issue: "SMTP disabled" in logs**

**Solution**:
- ✅ Set `SMTP_ENABLED=true`
- ✅ Restart backend service

---

## 📧 Supported Email Providers

### **Gmail (Recommended)**
```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

### **Outlook/Hotmail**
```env
SMTP_HOST=smtp-mail.outlook.com
SMTP_PORT=587
SMTP_USERNAME=your-email@outlook.com
SMTP_PASSWORD=your-password
```

### **Yahoo Mail**
```env
SMTP_HOST=smtp.mail.yahoo.com
SMTP_PORT=587
SMTP_USERNAME=your-email@yahoo.com
SMTP_PASSWORD=your-app-password
```

### **Custom SMTP Server**
```env
SMTP_HOST=mail.yourdomain.com
SMTP_PORT=587
SMTP_USERNAME=noreply@yourdomain.com
SMTP_PASSWORD=your-password
```

---

## 🎯 Development vs Production

### **Development Mode** (Current):
```env
SMTP_ENABLED=false
```
- OTP printed to backend logs
- No actual emails sent
- Good for testing without email setup

### **Production Mode**:
```env
SMTP_ENABLED=true
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```
- Actual emails sent to users
- Required for real user signups
- Use environment variables for security

---

## 🔒 Security Best Practices

### **DO**:
✅ Use App Passwords, never regular passwords  
✅ Store credentials in .env (add to .gitignore)  
✅ Use environment variables in production  
✅ Enable 2FA on email account  
✅ Rotate passwords regularly  

### **DON'T**:
❌ Commit .env file to Git  
❌ Share app passwords  
❌ Use personal email for production  
❌ Hard-code passwords in code  
❌ Use "Less secure app" access  

---

## 📝 Complete Configuration Example

### **1. Create .env file**:
```bash
cd storage-service
notepad .env
```

### **2. Add configuration**:
```env
# Copy ALL settings from .env.example and update these:

# Email/SMTP Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=yourproject@gmail.com
SMTP_PASSWORD=abcdefghijklmnop
SMTP_FROM_EMAIL=noreply@ictnexus.edu
SMTP_FROM_NAME=ICTNexus Storage
SMTP_ENABLED=true
```

### **3. Restart backend**:
```powershell
docker-compose -f docker-compose.storage.yml restart storage-service
```

### **4. Test signup**:
```
1. Go to http://localhost:5175/signup
2. Use your real email
3. Check inbox for OTP
4. Complete registration
```

---

## 🎊 Verification Checklist

After configuration, verify:

- [ ] .env file created in storage-service/
- [ ] SMTP_USERNAME set to your email
- [ ] SMTP_PASSWORD set to app password (16 chars)
- [ ] SMTP_ENABLED set to true
- [ ] Backend restarted
- [ ] Logs show "Email sent successfully"
- [ ] Test email received in inbox
- [ ] OTP code works in signup form

---

## 📚 Quick Reference

### Check if SMTP is enabled:
```powershell
docker logs storage_service | Select-String "SMTP"
```

### View OTP codes in logs:
```powershell
docker logs storage_service | Select-String "EMAIL OTP"
```

### Restart after config change:
```powershell
docker-compose -f docker-compose.storage.yml restart storage-service
```

### Test email sending:
```
1. Visit: http://localhost:5175/signup
2. Enter your email
3. Click "Continue to Verification"
4. Check your inbox
```

---

## 🆘 Still Not Working?

### **Development Workaround**:

Keep `SMTP_ENABLED=false` and get OTP from logs:

```powershell
# Start signup process
# Then immediately check logs:
docker logs storage_service --tail 5

# Look for line:
# [EMAIL OTP] To: test@gmail.com | Code: 123456

# Copy the code and enter in signup form
```

This works perfectly for development and demonstration!

---

## ✅ Summary

**To enable email sending**:

1. **Get Gmail App Password** (5 min)
2. **Create .env file** with SMTP settings (2 min)
3. **Set SMTP_ENABLED=true** (1 sec)
4. **Restart backend** (30 sec)
5. **Test signup** (2 min)

**For development/testing**:
- Keep `SMTP_ENABLED=false`
- Check logs for OTP codes
- Works perfectly without email setup!

---

**Current Status**: System works in both modes!  
**Development Mode**: ✅ OTP in logs  
**Production Mode**: Configure SMTP for real emails  

**You can demonstrate the full OTP flow right now using the logs!** 🚀
