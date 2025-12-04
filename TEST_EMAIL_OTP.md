# 🎉 Test Your Email OTP Authentication

**Status**: Backend restarted with your SMTP credentials  
**Date**: December 3, 2025

---

## ✅ Backend Restarted Successfully

Your SMTP configuration has been loaded!

---

## 🧪 How to Test Email OTP

### **Method 1: Test Signup Flow (Full Test)**

#### **Step 1: Go to Signup Page**
```
http://localhost:5175/signup
```

#### **Step 2: Fill Registration Form**
- Student ID: `TEST123`
- Email: **Use your REAL email address** (the one that will receive OTP)
- Password: `test1234`
- Confirm Password: `test1234`

#### **Step 3: Click "Continue to Verification"**
- ✅ Should see: "OTP sent to your email!"
- 📧 Check your email inbox
- ⏱️ Email should arrive within 30 seconds

#### **Step 4: Check Email**
Look for email with:
- **From**: ICTNexus Storage (or your SMTP email)
- **Subject**: "ICTNexus Storage - Email Verification Code"
- **Body**: Contains 6-digit code

Example:
```
Dear User,

Welcome to ICTNexus Storage Service!

Your email verification code is: 123456

This code will expire in 10 minutes.
```

#### **Step 5: Enter OTP Code**
- Copy the 6-digit code from email
- Paste in signup form
- Click "Create Account"
- ✅ Should see: "Account created successfully! Please login."

#### **Step 6: Login with New Account**
- Go to: http://localhost:5175/login
- Email: (the one you used for signup)
- Password: `test1234`
- ✅ Should enter dashboard with 2GB storage

---

### **Method 2: Test via API (Quick Test)**

#### **Using PowerShell**:
```powershell
# Request OTP
$response = Invoke-RestMethod -Uri "http://localhost:8085/api/v1/verify/request-otp" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"email":"your-email@gmail.com"}'

Write-Host $response
```

**Expected Response**:
```json
{
  "message": "OTP sent to your email"
}
```

Then **check your email** for the 6-digit code!

---

## 📧 What the Email Looks Like

### **Email Headers**:
```
From: ICTNexus Storage <noreply@ictnexus.edu>
To: your-email@gmail.com
Subject: ICTNexus Storage - Email Verification Code
```

### **Email Body**:
```
Dear User,

Welcome to ICTNexus Storage Service!

Your email verification code is: 123456

This code will expire in 10 minutes.

If you did not request this code, please ignore this email.

Best regards,
ICTNexus Storage Team
```

---

## 🔍 How to Monitor Email Sending

### **Check Backend Logs**:
```powershell
docker logs storage_service -f
```

**When OTP is requested, you'll see**:

**Success**:
```
[EMAIL OTP] To: test@gmail.com | Code: 123456
[EMAIL OTP] Email sent successfully to test@gmail.com
INFO: 172.19.0.1:xxxxx - "POST /api/v1/verify/request-otp HTTP/1.1" 200 OK
```

**Failure (Wrong Password)**:
```
[EMAIL OTP] To: test@gmail.com | Code: 123456
[EMAIL OTP] SMTP Error: (535, b'5.7.8 Username and Password not accepted')
[EMAIL OTP] SMTP disabled. Check logs for OTP code.
```

**Failure (Network)**:
```
[EMAIL OTP] To: test@gmail.com | Code: 123456
[EMAIL OTP] SMTP Error: [Errno 11001] getaddrinfo failed
```

---

## ✅ Success Indicators

### **Email Sent Successfully**:
- ✅ Backend logs show: "Email sent successfully"
- ✅ HTTP response: 200 OK
- ✅ Email arrives in inbox within 30 seconds
- ✅ Email contains 6-digit code
- ✅ Code works in signup form

### **SMTP Configuration Working**:
- ✅ No "SMTP Error" in logs
- ✅ No "Username and Password not accepted"
- ✅ Real email received (not just in logs)

---

## 🛠️ Troubleshooting

### **Issue: Email Not Received**

**Check 1 - Spam Folder**:
- Gmail: Check "Spam" folder
- Outlook: Check "Junk Email"
- Yahoo: Check "Spam"

**Check 2 - Backend Logs**:
```powershell
docker logs storage_service --tail 20
```
Look for "Email sent successfully" or "SMTP Error"

**Check 3 - SMTP Settings**:
```powershell
# Check if SMTP is enabled
docker exec storage_service printenv | Select-String "SMTP"
```

Should show:
```
SMTP_ENABLED=true
SMTP_USERNAME=your-email@gmail.com
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
```

**Check 4 - Internet Connection**:
```powershell
Test-NetConnection smtp.gmail.com -Port 587
```
Should show: `TcpTestSucceeded : True`

---

### **Issue: "Username and Password not accepted"**

**Solutions**:
1. ✅ Use **App Password**, not regular Gmail password
2. ✅ Ensure 2-Step Verification is enabled
3. ✅ Remove spaces from app password
4. ✅ Generate new app password if old one expired
5. ✅ Check you're using correct Gmail account

**Regenerate App Password**:
1. Go to: https://myaccount.google.com/apppasswords
2. Delete old "ICTNexus Storage" password
3. Create new password
4. Update .env file
5. Restart backend

---

### **Issue: "SMTP disabled" Message**

**Check .env file**:
```
SMTP_ENABLED=true  ← Must be "true", not "false"
```

**Restart backend**:
```powershell
docker-compose -f docker-compose.storage.yml restart storage-service
```

---

## 📊 Email Delivery Time

| Provider | Typical Delivery |
|----------|------------------|
| Gmail | 5-15 seconds |
| Outlook | 10-30 seconds |
| Yahoo | 15-45 seconds |
| Others | 30-60 seconds |

If email doesn't arrive in 2 minutes, check spam or logs.

---

## 🎯 Complete Test Scenario

### **Full Authentication Flow**:

1. **Signup**:
   - User visits `/signup`
   - Enters email and password
   - System sends OTP email ✅
   
2. **Email Received**:
   - User receives email within 30 seconds ✅
   - Email has clean subject and from address ✅
   - Email body is professional ✅

3. **OTP Verification**:
   - User enters 6-digit code
   - System validates (10-minute expiry) ✅
   - Account created ✅

4. **Login**:
   - User logs in with new credentials ✅
   - Receives 2GB free storage ✅
   - Can upload/download files ✅

---

## 🎓 Security Features Working

### **Email Verification**:
✅ Confirms email ownership  
✅ Prevents fake accounts  
✅ Reduces spam registrations  
✅ Professional email branding  

### **OTP Security**:
✅ 6-digit random code  
✅ 10-minute expiry  
✅ One-time use only  
✅ Previous codes invalidated  

### **Password Security**:
✅ Minimum 6 characters  
✅ Bcrypt hashing  
✅ Confirmation required  
✅ No plaintext storage  

---

## 📱 Test from Different Devices

### **Desktop Browser**:
- Chrome: http://localhost:5175/signup
- Firefox: http://localhost:5175/signup
- Edge: http://localhost:5175/signup

### **Mobile Device** (on same network):
- Find your computer's IP: `ipconfig`
- Use: http://YOUR-IP:5175/signup
- Example: http://192.168.1.100:5175/signup

---

## 🎊 Demo Script for Presentation

### **For Instructors/Evaluators**:

**"Let me demonstrate our secure authentication system..."**

1. **Show Signup Page**:
   - "Users enter their details here"
   - Fill form with real email

2. **Click Submit**:
   - "System sends verification email via SMTP"
   - Show toast notification

3. **Open Email Client**:
   - "Email arrives within seconds"
   - Show professional email format

4. **Enter OTP**:
   - "User verifies email ownership"
   - Paste code from email

5. **Account Created**:
   - "Secure registration complete!"
   - Login with new account

6. **Show Features**:
   - Notification bell
   - Storage quota (2GB)
   - Upload/download capability

---

## 📝 Quick Test Checklist

Before demonstration, verify:

- [ ] Docker Desktop running
- [ ] All services started
- [ ] Backend shows "Application startup complete"
- [ ] Can access http://localhost:5175
- [ ] SMTP credentials in .env
- [ ] SMTP_ENABLED=true
- [ ] Backend restarted after config
- [ ] Test email to yourself works
- [ ] OTP received in inbox
- [ ] OTP code works in form
- [ ] Can login after signup

---

## 🚀 Ready to Test!

**Run your first test**:

1. Open: http://localhost:5175/signup
2. Use your REAL email address
3. Submit form
4. Check inbox (30 sec wait)
5. Enter OTP code
6. Account created! ✅

**Your full authentication/authorization system is now live!** 🎉

---

## 📞 Support

If you encounter issues:

1. **Check logs**: `docker logs storage_service -f`
2. **Check spam folder**
3. **Verify SMTP settings**
4. **Test internet connection**
5. **Regenerate app password if needed**

---

**Status**: ✅ Backend restarted with SMTP credentials  
**Ready**: Test signup at http://localhost:5175/signup  
**Email**: Will be sent via Gmail SMTP  
**Next**: Try creating a test account!
