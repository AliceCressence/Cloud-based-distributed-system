"""
Email OTP Verification Models for User Registration
This allows new users to verify their email before activating their account
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from datetime import datetime, timedelta
from .database import Base


class EmailVerification(Base):
    """Email verification OTP tokens"""
    __tablename__ = "email_verifications"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, index=True)
    otp_code = Column(String(6))  # 6-digit OTP
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)  # OTP valid for 10 minutes
    is_used = Column(Boolean, default=False)
    verified_at = Column(DateTime, nullable=True)
    
    def is_expired(self) -> bool:
        """Check if OTP has expired"""
        return datetime.utcnow() > self.expires_at
    
    def is_valid(self) -> bool:
        """Check if OTP is valid for use"""
        return not self.is_used and not self.is_expired()
