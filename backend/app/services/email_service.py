"""
Email Service using Brevo SMTP
Handles all email notifications for the Axie Studio platform
"""

import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import List, Optional, Dict, Any
import logging
from jinja2 import Template

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        self.smtp_host = os.getenv('SMTP_HOST', 'smtp-relay.brevo.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.smtp_username = os.getenv('SMTP_USERNAME', '8abdb4001@smtp-brevo.com')
        self.smtp_password = os.getenv('SMTP_PASSWORD', 'cVzWUD1OPISBxAdv')
        self.from_email = os.getenv('FROM_EMAIL', 'noreply@axiestudio.se')
        self.from_name = os.getenv('FROM_NAME', 'Axie Studio')
        self.smtp_tls = os.getenv('SMTP_TLS', 'true').lower() == 'true'
        
    def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None,
        attachments: Optional[List[Dict[str, Any]]] = None
    ) -> bool:
        """
        Send email using Brevo SMTP
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            html_content: HTML email content
            text_content: Plain text content (optional)
            attachments: List of attachments (optional)
            
        Returns:
            bool: True if email sent successfully, False otherwise
        """
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = f"{self.from_name} <{self.from_email}>"
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Add text content
            if text_content:
                text_part = MIMEText(text_content, 'plain')
                msg.attach(text_part)
            
            # Add HTML content
            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)
            
            # Add attachments if any
            if attachments:
                for attachment in attachments:
                    self._add_attachment(msg, attachment)
            
            # Send email
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                if self.smtp_tls:
                    server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
            
            logger.info(f"Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return False
    
    def _add_attachment(self, msg: MIMEMultipart, attachment: Dict[str, Any]):
        """Add attachment to email message"""
        try:
            with open(attachment['path'], 'rb') as file:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(file.read())
                encoders.encode_base64(part)
                part.add_header(
                    'Content-Disposition',
                    f'attachment; filename= {attachment["filename"]}'
                )
                msg.attach(part)
        except Exception as e:
            logger.error(f"Failed to add attachment {attachment['filename']}: {str(e)}")
    
    def send_welcome_email(self, to_email: str, user_name: str) -> bool:
        """Send welcome email to new users"""
        subject = "Welcome to Axie Studio - Your AI Chat Platform"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Welcome to Axie Studio</title>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="text-align: center; margin-bottom: 30px;">
                    <img src="https://www.axiestudio.se/Axiestudiologo.jpg" alt="Axie Studio" style="max-width: 200px;">
                </div>
                
                <h1 style="color: #6366f1;">Welcome to Axie Studio, {user_name}!</h1>
                
                <p>Thank you for joining Axie Studio, the premier platform for AI-powered chat widgets.</p>
                
                <div style="background: #f8fafc; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <h3 style="color: #6366f1; margin-top: 0;">What's Next?</h3>
                    <ul>
                        <li>🎨 <strong>Customize your chat widget</strong> - Make it match your brand</li>
                        <li>📊 <strong>Track conversations</strong> - Monitor engagement and performance</li>
                        <li>⭐ <strong>Upgrade to Premium</strong> - Remove "Powered by Axie Studio" for $49/month</li>
                        <li>🚀 <strong>Embed anywhere</strong> - Add to your website with one line of code</li>
                    </ul>
                </div>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="https://chat.axiestudio.se/admin/login" 
                       style="background: #6366f1; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; display: inline-block;">
                        Access Your Dashboard
                    </a>
                </div>
                
                <p>Need help? Reply to this email or visit our support center.</p>
                
                <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 30px 0;">
                <p style="font-size: 14px; color: #6b7280;">
                    Best regards,<br>
                    The Axie Studio Team<br>
                    <a href="https://axiestudio.se">axiestudio.se</a>
                </p>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
        Welcome to Axie Studio, {user_name}!
        
        Thank you for joining Axie Studio, the premier platform for AI-powered chat widgets.
        
        What's Next?
        - Customize your chat widget
        - Track conversations and performance
        - Upgrade to Premium to remove branding ($49/month)
        - Embed your widget anywhere with one line of code
        
        Access your dashboard: https://chat.axiestudio.se/admin/login
        
        Need help? Reply to this email or visit our support center.
        
        Best regards,
        The Axie Studio Team
        https://axiestudio.se
        """
        
        return self.send_email(to_email, subject, html_content, text_content)
    
    def send_payment_confirmation(self, to_email: str, user_name: str, plan_name: str, amount: float) -> bool:
        """Send payment confirmation email"""
        subject = f"Payment Confirmed - {plan_name} Plan Activated"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Payment Confirmed</title>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="text-align: center; margin-bottom: 30px;">
                    <img src="https://www.axiestudio.se/Axiestudiologo.jpg" alt="Axie Studio" style="max-width: 200px;">
                </div>
                
                <h1 style="color: #10b981;">Payment Confirmed!</h1>
                
                <p>Hi {user_name},</p>
                
                <p>Your payment has been successfully processed and your <strong>{plan_name}</strong> plan is now active.</p>
                
                <div style="background: #f0fdf4; border: 1px solid #10b981; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <h3 style="color: #10b981; margin-top: 0;">Payment Details</h3>
                    <p><strong>Plan:</strong> {plan_name}</p>
                    <p><strong>Amount:</strong> ${amount:.2f}/month</p>
                    <p><strong>Status:</strong> Active</p>
                    {"<p><strong>Branding:</strong> Removed from your chat widgets</p>" if plan_name != "Free" else ""}
                </div>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="https://chat.axiestudio.se/admin/billing" 
                       style="background: #6366f1; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; display: inline-block;">
                        Manage Subscription
                    </a>
                </div>
                
                <p>Thank you for choosing Axie Studio!</p>
                
                <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 30px 0;">
                <p style="font-size: 14px; color: #6b7280;">
                    Best regards,<br>
                    The Axie Studio Team<br>
                    <a href="https://axiestudio.se">axiestudio.se</a>
                </p>
            </div>
        </body>
        </html>
        """
        
        return self.send_email(to_email, subject, html_content)
    
    def send_subscription_cancelled(self, to_email: str, user_name: str) -> bool:
        """Send subscription cancellation email"""
        subject = "Subscription Cancelled - We're Sorry to See You Go"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Subscription Cancelled</title>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="text-align: center; margin-bottom: 30px;">
                    <img src="https://www.axiestudio.se/Axiestudiologo.jpg" alt="Axie Studio" style="max-width: 200px;">
                </div>
                
                <h1 style="color: #ef4444;">Subscription Cancelled</h1>
                
                <p>Hi {user_name},</p>
                
                <p>We're sorry to see you go! Your subscription has been cancelled as requested.</p>
                
                <div style="background: #fef2f2; border: 1px solid #ef4444; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <h3 style="color: #ef4444; margin-top: 0;">What Happens Next?</h3>
                    <ul>
                        <li>Your account will remain active until the end of your billing period</li>
                        <li>After that, you'll be moved to the free plan</li>
                        <li>"Powered by Axie Studio" branding will return to your widgets</li>
                        <li>You can reactivate anytime from your dashboard</li>
                    </ul>
                </div>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="https://chat.axiestudio.se/admin/billing" 
                       style="background: #6366f1; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; display: inline-block;">
                        Reactivate Subscription
                    </a>
                </div>
                
                <p>We'd love to have you back! If you have any feedback, please reply to this email.</p>
                
                <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 30px 0;">
                <p style="font-size: 14px; color: #6b7280;">
                    Best regards,<br>
                    The Axie Studio Team<br>
                    <a href="https://axiestudio.se">axiestudio.se</a>
                </p>
            </div>
        </body>
        </html>
        """
        
        return self.send_email(to_email, subject, html_content)

# Global email service instance
email_service = EmailService()
