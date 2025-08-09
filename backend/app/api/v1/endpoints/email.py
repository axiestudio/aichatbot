"""
Email API endpoints for testing and notifications
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from typing import Optional
import logging

from ....services.email_service import email_service

logger = logging.getLogger(__name__)

router = APIRouter()

class EmailTestRequest(BaseModel):
    to_email: EmailStr
    subject: str
    message: str

class WelcomeEmailRequest(BaseModel):
    to_email: EmailStr
    user_name: str

class PaymentConfirmationRequest(BaseModel):
    to_email: EmailStr
    user_name: str
    plan_name: str
    amount: float

@router.post("/test")
async def send_test_email(request: EmailTestRequest):
    """
    Send a test email to verify SMTP configuration
    """
    try:
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Test Email</title>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="text-align: center; margin-bottom: 30px;">
                    <img src="https://www.axiestudio.se/Axiestudiologo.jpg" alt="Axie Studio" style="max-width: 200px;">
                </div>
                
                <h1 style="color: #6366f1;">Test Email from Axie Studio</h1>
                
                <p>{request.message}</p>
                
                <div style="background: #f8fafc; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <p><strong>SMTP Configuration Test</strong></p>
                    <p>✅ Brevo SMTP is working correctly!</p>
                    <p>✅ Email service is configured properly</p>
                    <p>✅ Ready for production notifications</p>
                </div>
                
                <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 30px 0;">
                <p style="font-size: 14px; color: #6b7280;">
                    This is a test email from Axie Studio<br>
                    <a href="https://axiestudio.se">axiestudio.se</a>
                </p>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
        Test Email from Axie Studio
        
        {request.message}
        
        SMTP Configuration Test:
        ✅ Brevo SMTP is working correctly!
        ✅ Email service is configured properly
        ✅ Ready for production notifications
        
        This is a test email from Axie Studio
        https://axiestudio.se
        """
        
        success = email_service.send_email(
            to_email=request.to_email,
            subject=request.subject,
            html_content=html_content,
            text_content=text_content
        )
        
        if success:
            return {"success": True, "message": "Test email sent successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to send test email")
            
    except Exception as e:
        logger.error(f"Failed to send test email: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Email sending failed: {str(e)}")

@router.post("/welcome")
async def send_welcome_email(request: WelcomeEmailRequest):
    """
    Send welcome email to new users
    """
    try:
        success = email_service.send_welcome_email(
            to_email=request.to_email,
            user_name=request.user_name
        )
        
        if success:
            return {"success": True, "message": "Welcome email sent successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to send welcome email")
            
    except Exception as e:
        logger.error(f"Failed to send welcome email: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Welcome email failed: {str(e)}")

@router.post("/payment-confirmation")
async def send_payment_confirmation_email(request: PaymentConfirmationRequest):
    """
    Send payment confirmation email
    """
    try:
        success = email_service.send_payment_confirmation(
            to_email=request.to_email,
            user_name=request.user_name,
            plan_name=request.plan_name,
            amount=request.amount
        )
        
        if success:
            return {"success": True, "message": "Payment confirmation email sent successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to send payment confirmation email")
            
    except Exception as e:
        logger.error(f"Failed to send payment confirmation email: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Payment confirmation email failed: {str(e)}")

@router.get("/status")
async def get_email_service_status():
    """
    Get email service configuration status
    """
    try:
        import os
        
        config = {
            "smtp_host": os.getenv('SMTP_HOST'),
            "smtp_port": os.getenv('SMTP_PORT'),
            "smtp_username": os.getenv('SMTP_USERNAME'),
            "from_email": os.getenv('FROM_EMAIL'),
            "from_name": os.getenv('FROM_NAME'),
            "smtp_configured": bool(os.getenv('SMTP_HOST') and os.getenv('SMTP_USERNAME') and os.getenv('SMTP_PASSWORD'))
        }
        
        return {
            "success": True,
            "message": "Email service status",
            "config": config
        }
        
    except Exception as e:
        logger.error(f"Failed to get email service status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Status check failed: {str(e)}")
