"""
Email Verification Routes
Handles OTP-based email verification for new user registration
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from ..database import get_db
from ..services.email_service import EmailService

router = APIRouter(prefix="/verify", tags=["Email Verification"])


class EmailRequest(BaseModel):
    email: str


class OTPVerifyRequest(BaseModel):
    email: str
    otp_code: str


@router.post("/request-otp")
def request_otp(request: EmailRequest, db: Session = Depends(get_db)):
    """
    Request an OTP code for email verification
    
    Used during user registration to verify email ownership
    """
    try:
        message = EmailService.request_otp(db, request.email)
        return {
            "success": True,
            "message": message,
            "email": request.email
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/verify-otp")
def verify_otp(request: OTPVerifyRequest, db: Session = Depends(get_db)):
    """
    Verify an OTP code
    
    Returns success if OTP is valid and not expired
    """
    try:
        is_valid = EmailService.verify_otp(db, request.email, request.otp_code)
        return {
            "success": True,
            "message": "Email verified successfully",
            "email": request.email
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/resend-otp")
def resend_otp(request: EmailRequest, db: Session = Depends(get_db)):
    """
    Resend OTP code to email
    
    Invalidates previous OTP and sends a new one
    """
    try:
        message = EmailService.request_otp(db, request.email)
        return {
            "success": True,
            "message": "New OTP sent to your email",
            "email": request.email
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
