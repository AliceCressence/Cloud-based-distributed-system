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
        # Email configuration (you'll need to set these in your environment)
        try:
            msg = MIMEMultipart()
            msg['From'] = settings.smtp_from_email if hasattr(settings, 'smtp_from_email') else "noreply@ictnexus.edu"
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
            
            # For development, just log the OTP instead of sending
            # In production, configure SMTP settings
            print(f"[EMAIL OTP] To: {email} | Code: {otp_code}")
            
            # Uncomment below for production SMTP sending
            # if hasattr(settings, 'smtp_host'):
            #     with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
            #         if hasattr(settings, 'smtp_username'):
            #             server.login(settings.smtp_username, settings.smtp_password)
            #         server.send_message(msg)
            
        except Exception as e:
            print(f"Error sending email: {e}")
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
