"""
Email OTP Service for User Verification
Sends OTP codes to users for email verification during registration
"""
import random
import string
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from fastapi import HTTPException
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from ..models_otp import EmailVerification
from ..config import get_settings

settings = get_settings()


class EmailService:
    """Service for managing email OTP verification"""
    
    @staticmethod
    def generate_otp() -> str:
        """Generate a 6-digit OTP code"""
        return ''.join(random.choices(string.digits, k=6))
    
    @staticmethod
    def create_verification(db: Session, email: str) -> EmailVerification:
        """Create a new email verification OTP"""
        # Invalidate any existing OTPs for this email
        db.query(EmailVerification).filter(
            EmailVerification.email == email,
            EmailVerification.is_used == False
        ).update({"is_used": True})
        
        otp_code = EmailService.generate_otp()
        expires_at = datetime.utcnow() + timedelta(minutes=10)
        
        verification = EmailVerification(
            email=email,
            otp_code=otp_code,
            expires_at=expires_at
        )
        db.add(verification)
        db.commit()
        db.refresh(verification)
        
        return verification
    
    @staticmethod
    def send_otp_email(email: str, otp_code: str):
        """Send OTP code via email"""
        try:
            msg = MIMEMultipart()
            msg['From'] = f"{settings.smtp_from_name} <{settings.smtp_from_email}>"
            msg['To'] = email
            msg['Subject'] = "ICTNexus Storage - Email Verification Code"
            
            body = f"""
Dear User,

Welcome to ICTNexus Storage Service!

Your email verification code is: {otp_code}

This code will expire in 10 minutes.

If you did not request this code, please ignore this email.

Best regards,
ICTNexus Storage Team
"""
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Always log the OTP for development/debugging
            print(f"[EMAIL OTP] To: {email} | Code: {otp_code}")
            
            # Send via SMTP if enabled
            if settings.smtp_enabled and settings.smtp_username and settings.smtp_password:
                try:
                    with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
                        server.starttls()  # Enable TLS
                        server.login(settings.smtp_username, settings.smtp_password)
                        server.send_message(msg)
                    print(f"[EMAIL OTP] Email sent successfully to {email}")
                except Exception as smtp_error:
                    print(f"[EMAIL OTP] SMTP Error: {smtp_error}")
                    # Still log to console so OTP is accessible
            else:
                print(f"[EMAIL OTP] SMTP disabled. Check logs for OTP code.")
            
        except Exception as e:
            print(f"[EMAIL OTP] Error: {e}")
            # Don't fail registration if email fails
            pass
    
    @staticmethod
    def verify_otp(db: Session, email: str, otp_code: str) -> bool:
        """Verify an OTP code"""
        verification = db.query(EmailVerification).filter(
            EmailVerification.email == email,
            EmailVerification.otp_code == otp_code,
            EmailVerification.is_used == False
        ).first()
        
        if not verification:
            raise HTTPException(status_code=400, detail="Invalid OTP code")
        
        if verification.is_expired():
            raise HTTPException(status_code=400, detail="OTP code has expired")
        
        # Mark as used
        verification.is_used = True
        verification.verified_at = datetime.utcnow()
        db.commit()
        
        return True
    
    @staticmethod
    def request_otp(db: Session, email: str) -> str:
        """Request a new OTP for email verification"""
        verification = EmailService.create_verification(db, email)
        EmailService.send_otp_email(email, verification.otp_code)
        return "OTP sent to your email"
