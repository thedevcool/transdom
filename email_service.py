"""
Email Service for sending transactional emails
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
import os
from datetime import datetime
from config import FRONTEND_URL


class ZohoEmailService:
    """Service for sending emails via Zoho Mail SMTP"""
    
    def __init__(self):
        """Initialize Zoho email configuration"""
        self.smtp_server = os.getenv("ZOHO_SMTP_SERVER", "smtp.zoho.com")
        self.smtp_port = int(os.getenv("ZOHO_SMTP_PORT", "587"))
        self.sender_email = os.getenv("ZOHO_SENDER_EMAIL")
        self.sender_password = os.getenv("ZOHO_SENDER_PASSWORD")
        self.sender_name = os.getenv("ZOHO_SENDER_NAME", "Transdom Express")
        self.frontend_url = FRONTEND_URL
        
        if not self.sender_email or not self.sender_password:
            raise ValueError("ZOHO_SENDER_EMAIL and ZOHO_SENDER_PASSWORD must be set in environment")
    
    def _send_email(self, to_email: str, subject: str, html_body: str) -> bool:
        """
        Send an email using Zoho SMTP
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            html_body: HTML content of the email
            
        Returns:
            True if email sent successfully, False otherwise
        """
        try:
            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = f"{self.sender_name} <{self.sender_email}>"
            message["To"] = to_email
            
            # Attach HTML content
            html_part = MIMEText(html_body, "html")
            message.attach(html_part)
            
            # Connect to Zoho SMTP server
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(message)
            
            return True
            
        except Exception as e:
            print(f"Failed to send email to {to_email}: {str(e)}")
            return False
    
    def send_welcome_email(self, user_email: str, user_name: str) -> bool:
        """
        Send welcome email to new user
        
        Args:
            user_email: User's email address
            user_name: User's first name
            
        Returns:
            True if email sent successfully
        """
        subject = "Welcome to Transdom Express! 🚀"
        
        html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f3f4f6;">
    <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #f3f4f6; padding: 40px 20px;">
        <tr>
            <td align="center">
                <table width="600" cellpadding="0" cellspacing="0" style="background-color: #ffffff; border-radius: 16px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                    <!-- Header -->
                    <tr>
                        <td style="background: linear-gradient(135deg, #FCD34D 0%, #F59E0B 100%); padding: 50px 40px; text-align: center;">
                            <h1 style="color: #78350F; margin: 0; font-size: 32px; font-weight: 700; text-shadow: 1px 1px 2px rgba(255,255,255,0.3);">
                                🍋 Welcome to Transdom Express!
                            </h1>
                        </td>
                    </tr>
                    
                    <!-- Body -->
                    <tr>
                        <td style="padding: 40px; background-color: #FFFBEB;">
                            <p style="font-size: 18px; color: #1F2937; margin: 0 0 20px 0;">
                                Hi <strong style="color: #F59E0B;">{user_name}</strong>,
                            </p>
                            
                            <p style="font-size: 16px; color: #4B5563; line-height: 1.6; margin: 0 0 25px 0;">
                                Thank you for joining Transdom Express! We're thrilled to have you on board. 
                                Your account is now active and ready to use.
                            </p>
                            
                            <!-- Features Card -->
                            <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #ffffff; border-radius: 12px; border: 2px solid #FCD34D; margin: 25px 0;">
                                <tr>
                                    <td style="padding: 30px;">
                                        <h3 style="margin: 0 0 20px 0; color: #F59E0B; font-size: 20px; font-weight: 600;">
                                            🎯 What You Can Do Now:
                                        </h3>
                                        <table width="100%" cellpadding="0" cellspacing="0">
                                            <tr>
                                                <td style="padding: 8px 0;">
                                                    <span style="color: #FCD34D; font-size: 18px; margin-right: 10px;">✓</span>
                                                    <span style="color: #4B5563; font-size: 15px;">Calculate shipping rates to 8 global zones</span>
                                                </td>
                                            </tr>
                                            <tr>
                                                <td style="padding: 8px 0;">
                                                    <span style="color: #FCD34D; font-size: 18px; margin-right: 10px;">✓</span>
                                                    <span style="color: #4B5563; font-size: 15px;">Create and track your shipments in real-time</span>
                                                </td>
                                            </tr>
                                            <tr>
                                                <td style="padding: 8px 0;">
                                                    <span style="color: #FCD34D; font-size: 18px; margin-right: 10px;">✓</span>
                                                    <span style="color: #4B5563; font-size: 15px;">Get instant order status updates</span>
                                                </td>
                                            </tr>
                                            <tr>
                                                <td style="padding: 8px 0;">
                                                    <span style="color: #FCD34D; font-size: 18px; margin-right: 10px;">✓</span>
                                                    <span style="color: #4B5563; font-size: 15px;">Access complete shipping history</span>
                                                </td>
                                            </tr>
                                        </table>
                                    </td>
                                </tr>
                            </table>
                            
                            <p style="font-size: 16px; color: #4B5563; line-height: 1.6; margin: 25px 0;">
                                Ready to send your first package? Click the button below to get started!
                            </p>
                            
                            <!-- CTA Button -->
                            <table width="100%" cellpadding="0" cellspacing="0" style="margin: 30px 0;">
                                <tr>
                                    <td align="center">
                                        <a href="{self.frontend_url}" style="display: inline-block; background: linear-gradient(135deg, #FCD34D 0%, #F59E0B 100%); color: #78350F; padding: 16px 40px; text-decoration: none; border-radius: 30px; font-weight: 700; font-size: 16px; box-shadow: 0 4px 12px rgba(252, 211, 77, 0.4); transition: transform 0.2s;">
                                            🚀 Get Started Now
                                        </a>
                                    </td>
                                </tr>
                            </table>
                            
                            <p style="font-size: 14px; color: #6B7280; margin: 25px 0 0 0; text-align: center;">
                                Need help? Our support team is here for you 24/7
                            </p>
                        </td>
                    </tr>
                    
                    <!-- Footer -->
                    <tr>
                        <td style="background-color: #1F2937; padding: 30px; text-align: center;">
                            <p style="margin: 0; font-size: 13px; color: #9CA3AF;">
                                © {datetime.now().year} Transdom Express. All rights reserved.
                            </p>
                            <p style="margin: 10px 0 0 0; font-size: 12px; color: #6B7280;">
                                Fast, Reliable, Global Shipping Solutions
                            </p>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>
        """
        
        return self._send_email(user_email, subject, html_body)
    
    def send_order_confirmation_email(
        self,
        user_email: str,
        user_name: str,
        order_no: str,
        order_details: dict
    ) -> bool:
        """
        Send order confirmation email to user
        
        Args:
            user_email: User's email address
            user_name: User's first name
            order_no: Order number
            order_details: Order information dict
            
        Returns:
            True if email sent successfully
        """
        subject = f"Order Confirmation - {order_no}"
        
        # Extract order details
        sender = order_details.get("sender", {})
        receiver = order_details.get("receiver", {})
        shipment = order_details.get("shipment", {})
        pricing = order_details.get("pricing", {})
        
        html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f3f4f6;">
    <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #f3f4f6; padding: 40px 20px;">
        <tr>
            <td align="center">
                <table width="600" cellpadding="0" cellspacing="0" style="background-color: #ffffff; border-radius: 16px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                    <!-- Header -->
                    <tr>
                        <td style="background: linear-gradient(135deg, #FCD34D 0%, #F59E0B 100%); padding: 50px 40px; text-align: center;">
                            <h1 style="color: #78350F; margin: 0; font-size: 32px; font-weight: 700; text-shadow: 1px 1px 2px rgba(255,255,255,0.3);">
                                📦 Order Received!
                            </h1>
                        </td>
                    </tr>
                    
                    <!-- Body -->
                    <tr>
                        <td style="padding: 40px; background-color: #FFFBEB;">
                            <p style="font-size: 18px; color: #1F2937; margin: 0 0 20px 0;">
                                Hi <strong style="color: #F59E0B;">{user_name}</strong>,
                            </p>
                            
                            <p style="font-size: 16px; color: #4B5563; line-height: 1.6; margin: 0 0 25px 0;">
                                Thank you for your order! We've received your shipment request and it's being processed.
                            </p>
                            
                            <!-- Status Alert -->
                            <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #FEF3C7; border: 2px solid #F59E0B; border-radius: 12px; margin: 25px 0;">
                                <tr>
                                    <td style="padding: 20px; text-align: center;">
                                        <p style="margin: 0; color: #78350F; font-size: 16px; font-weight: 600;">
                                            ⏳ <strong>Status:</strong> Pending Admin Approval
                                        </p>
                                    </td>
                                </tr>
                            </table>
                            
                            <!-- Order Details Card -->
                            <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #ffffff; border-radius: 12px; border: 2px solid #FCD34D; margin: 25px 0;">
                                <tr>
                                    <td style="padding: 30px;">
                                        <h3 style="margin: 0 0 20px 0; color: #F59E0B; font-size: 20px; font-weight: 600;">📋 Order Details</h3>
                                        <table width="100%" cellpadding="0" cellspacing="0">
                                            <tr>
                                                <td style="padding: 10px 0; border-bottom: 1px solid #FEF3C7; color: #4B5563;"><strong>Order Number:</strong></td>
                                                <td style="padding: 10px 0; border-bottom: 1px solid #FEF3C7; color: #1F2937; text-align: right;">{order_no}</td>
                                            </tr>
                                            <tr>
                                                <td style="padding: 10px 0; border-bottom: 1px solid #FEF3C7; color: #4B5563;"><strong>Order Date:</strong></td>
                                                <td style="padding: 10px 0; border-bottom: 1px solid #FEF3C7; color: #1F2937; text-align: right;">{datetime.now().strftime("%B %d, %Y at %I:%M %p")}</td>
                                            </tr>
                                            <tr>
                                                <td style="padding: 10px 0; border-bottom: 1px solid #FEF3C7; color: #4B5563;"><strong>Destination Zone:</strong></td>
                                                <td style="padding: 10px 0; border-bottom: 1px solid #FEF3C7; color: #1F2937; text-align: right;">{shipment.get('destination_zone', 'N/A')}</td>
                                            </tr>
                                            <tr>
                                                <td style="padding: 10px 0; color: #4B5563;"><strong>Weight:</strong></td>
                                                <td style="padding: 10px 0; color: #1F2937; text-align: right;">{shipment.get('weight', 'N/A')} kg</td>
                                            </tr>
                                        </table>
                                    </td>
                                </tr>
                            </table>
                            
                            <!-- Shipping Info Card -->
                            <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #ffffff; border-radius: 12px; border: 2px solid #FCD34D; margin: 25px 0;">
                                <tr>
                                    <td style="padding: 30px;">
                                        <h3 style="margin: 0 0 20px 0; color: #F59E0B; font-size: 20px; font-weight: 600;">📍 Shipping Information</h3>
                                        <div style="margin-bottom: 20px; padding: 15px; background-color: #FFFBEB; border-radius: 8px;">
                                            <p style="margin: 0 0 5px 0; color: #78350F; font-weight: 600; font-size: 14px;">FROM:</p>
                                            <p style="margin: 0; color: #4B5563; font-size: 14px; line-height: 1.6;">
                                                {sender.get('name', 'N/A')}<br>
                                                {sender.get('address', 'N/A')}<br>
                                                {sender.get('city', '')}, {sender.get('country', '')}<br>
                                                📞 {sender.get('phone', 'N/A')}
                                            </p>
                                        </div>
                                        <div style="padding: 15px; background-color: #FFFBEB; border-radius: 8px;">
                                            <p style="margin: 0 0 5px 0; color: #78350F; font-weight: 600; font-size: 14px;">TO:</p>
                                            <p style="margin: 0; color: #4B5563; font-size: 14px; line-height: 1.6;">
                                                {receiver.get('name', 'N/A')}<br>
                                                {receiver.get('address', 'N/A')}<br>
                                                {receiver.get('city', '')}, {receiver.get('country', '')}<br>
                                                📞 {receiver.get('phone', 'N/A')}
                                            </p>
                                        </div>
                                    </td>
                                </tr>
                            </table>
                            
                            <!-- Pricing Card -->
                            <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #ffffff; border-radius: 12px; border: 2px solid #FCD34D; margin: 25px 0;">
                                <tr>
                                    <td style="padding: 30px;">
                                        <h3 style="margin: 0 0 20px 0; color: #F59E0B; font-size: 20px; font-weight: 600;">💰 Pricing Summary</h3>
                                        <table width="100%" cellpadding="0" cellspacing="0">
                                            <tr>
                                                <td style="padding: 10px 0; border-bottom: 1px solid #FEF3C7; color: #4B5563;">Shipping Fee:</td>
                                                <td style="padding: 10px 0; border-bottom: 1px solid #FEF3C7; color: #1F2937; text-align: right;">₦{pricing.get('shipping_fee', '0.00')}</td>
                                            </tr>
                                            <tr>
                                                <td style="padding: 10px 0; border-bottom: 1px solid #FEF3C7; color: #4B5563;">Insurance Fee:</td>
                                                <td style="padding: 10px 0; border-bottom: 1px solid #FEF3C7; color: #1F2937; text-align: right;">₦{pricing.get('insurance_fee', '0.00')}</td>
                                            </tr>
                                            <tr style="background-color: #FEF3C7;">
                                                <td style="padding: 16px 10px; font-weight: 700; font-size: 18px; color: #78350F;">Total Amount:</td>
                                                <td style="padding: 16px 10px; font-weight: 700; font-size: 20px; color: #F59E0B; text-align: right;">₦{pricing.get('total_amount', '0.00')}</td>
                                            </tr>
                                        </table>
                                    </td>
                                </tr>
                            </table>
                            
                            <p style="font-size: 15px; color: #4B5563; line-height: 1.6; margin: 25px 0; text-align: center;">
                                We'll send you another email once your order has been approved by our team. 📧
                            </p>
                            
                            <!-- Track Order Button -->
                            <table width="100%" cellpadding="0" cellspacing="0" style="margin: 30px 0;">
                                <tr>
                                    <td align="center">
                                        <a href="{self.frontend_url}/orders" style="display: inline-block; background: linear-gradient(135deg, #FCD34D 0%, #F59E0B 100%); color: #78350F; padding: 14px 35px; text-decoration: none; border-radius: 30px; font-weight: 700; font-size: 15px; box-shadow: 0 4px 12px rgba(252, 211, 77, 0.4);">
                                            📦 Track Order
                                        </a>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                    
                    <!-- Footer -->
                    <tr>
                        <td style="background-color: #1F2937; padding: 30px; text-align: center;">
                            <p style="margin: 0; font-size: 13px; color: #9CA3AF;">
                                © {datetime.now().year} Transdom Express. All rights reserved.
                            </p>
                            <p style="margin: 10px 0 0 0; font-size: 12px; color: #6B7280;">
                                Fast, Reliable, Global Shipping Solutions
                            </p>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>
        """
        
        return self._send_email(user_email, subject, html_body)
    
    def send_order_approval_email(
        self,
        user_email: str,
        user_name: str,
        order_no: str,
        order_details: dict,
        status: str
    ) -> bool:
        """
        Send order approval/rejection email with receipt
        
        Args:
            user_email: User's email address
            user_name: User's first name
            order_no: Order number
            order_details: Order information dict
            status: Order status (approved/rejected)
            
        Returns:
            True if email sent successfully
        """
        if status.lower() == "approved":
            subject = f"Order Approved - {order_no} ✅"
            status_color = "#28a745"
            status_text = "Approved"
            status_message = "Great news! Your shipment order has been approved and is being processed."
            status_icon = "✅"
            status_bg = "#d4edda"
        else:
            subject = f"Order Update - {order_no}"
            status_color = "#dc3545"
            status_text = "Rejected"
            status_message = "Unfortunately, your shipment order has been rejected. Please contact support for more information."
            status_icon = "❌"
            status_bg = "#f8d7da"
        
        # Extract order details
        sender = order_details.get("sender", {})
        receiver = order_details.get("receiver", {})
        shipment = order_details.get("shipment", {})
        pricing = order_details.get("pricing", {})
        payment = order_details.get("payment", {})
        
        html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
        <h1 style="color: white; margin: 0; font-size: 28px;">Order {status_text} {status_icon}</h1>
    </div>
    
    <div style="background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px;">
        <p style="font-size: 16px; margin-bottom: 20px;">Hi <strong>{user_name}</strong>,</p>
        
        <div style="background: {status_bg}; border: 1px solid {status_color}; padding: 15px; border-radius: 5px; margin: 20px 0;">
            <p style="margin: 0; color: {status_color};">
                <strong>{status_icon} {status_text}:</strong> {status_message}
            </p>
        </div>
        
        <div style="background: white; padding: 20px; border: 2px solid #667eea; border-radius: 5px; margin: 20px 0;">
            <h2 style="margin-top: 0; color: #667eea; text-align: center; border-bottom: 2px solid #667eea; padding-bottom: 10px;">
                SHIPMENT RECEIPT
            </h2>
            
            <table style="width: 100%; border-collapse: collapse; margin-top: 20px;">
                <tr>
                    <td style="padding: 8px 0; border-bottom: 1px solid #eee;"><strong>Order Number:</strong></td>
                    <td style="padding: 8px 0; border-bottom: 1px solid #eee;">{order_no}</td>
                </tr>
                <tr>
                    <td style="padding: 8px 0; border-bottom: 1px solid #eee;"><strong>Order Date:</strong></td>
                    <td style="padding: 8px 0; border-bottom: 1px solid #eee;">{order_details.get('created_at', 'N/A')}</td>
                </tr>
                <tr>
                    <td style="padding: 8px 0; border-bottom: 1px solid #eee;"><strong>Status:</strong></td>
                    <td style="padding: 8px 0; border-bottom: 1px solid #eee; color: {status_color}; font-weight: bold;">{status_text}</td>
                </tr>
            </table>
            
            <h3 style="color: #667eea; margin-top: 25px; margin-bottom: 10px;">Shipment Details</h3>
            <table style="width: 100%; border-collapse: collapse;">
                <tr>
                    <td style="padding: 8px 0; border-bottom: 1px solid #eee;">Destination Zone:</td>
                    <td style="padding: 8px 0; border-bottom: 1px solid #eee;">{shipment.get('destination_zone', 'N/A')}</td>
                </tr>
                <tr>
                    <td style="padding: 8px 0; border-bottom: 1px solid #eee;">Weight:</td>
                    <td style="padding: 8px 0; border-bottom: 1px solid #eee;">{shipment.get('weight', 'N/A')} kg</td>
                </tr>
                <tr>
                    <td style="padding: 8px 0; border-bottom: 1px solid #eee;">Package Type:</td>
                    <td style="padding: 8px 0; border-bottom: 1px solid #eee;">{shipment.get('package_type', 'N/A')}</td>
                </tr>
                <tr>
                    <td style="padding: 8px 0; border-bottom: 1px solid #eee;">Contents:</td>
                    <td style="padding: 8px 0; border-bottom: 1px solid #eee;">{shipment.get('contents_description', 'N/A')}</td>
                </tr>
            </table>
            
            <h3 style="color: #667eea; margin-top: 25px; margin-bottom: 10px;">Sender Information</h3>
            <p style="margin: 5px 0; line-height: 1.8;">
                <strong>Name:</strong> {sender.get('name', 'N/A')}<br>
                <strong>Phone:</strong> {sender.get('phone', 'N/A')}<br>
                <strong>Address:</strong> {sender.get('address', 'N/A')}<br>
                <strong>City:</strong> {sender.get('city', 'N/A')}<br>
                <strong>Country:</strong> {sender.get('country', 'N/A')}
            </p>
            
            <h3 style="color: #667eea; margin-top: 25px; margin-bottom: 10px;">Receiver Information</h3>
            <p style="margin: 5px 0; line-height: 1.8;">
                <strong>Name:</strong> {receiver.get('name', 'N/A')}<br>
                <strong>Phone:</strong> {receiver.get('phone', 'N/A')}<br>
                <strong>Address:</strong> {receiver.get('address', 'N/A')}<br>
                <strong>City:</strong> {receiver.get('city', 'N/A')}<br>
                <strong>Country:</strong> {receiver.get('country', 'N/A')}
            </p>
            
            <h3 style="color: #667eea; margin-top: 25px; margin-bottom: 10px;">Payment Details</h3>
            <table style="width: 100%; border-collapse: collapse;">
                <tr>
                    <td style="padding: 8px 0; border-bottom: 1px solid #eee;">Payment Method:</td>
                    <td style="padding: 8px 0; border-bottom: 1px solid #eee;">{payment.get('payment_method', 'N/A')}</td>
                </tr>
                <tr>
                    <td style="padding: 8px 0; border-bottom: 1px solid #eee;">Reference:</td>
                    <td style="padding: 8px 0; border-bottom: 1px solid #eee;">{payment.get('reference', 'N/A')}</td>
                </tr>
            </table>
            
            <h3 style="color: #667eea; margin-top: 25px; margin-bottom: 10px;">Cost Breakdown</h3>
            <table style="width: 100%; border-collapse: collapse;">
                <tr>
                    <td style="padding: 8px 0; border-bottom: 1px solid #eee;">Shipping Fee:</td>
                    <td style="padding: 8px 0; border-bottom: 1px solid #eee; text-align: right;">₦{pricing.get('shipping_fee', '0.00')}</td>
                </tr>
                <tr>
                    <td style="padding: 8px 0; border-bottom: 1px solid #eee;">Insurance Fee:</td>
                    <td style="padding: 8px 0; border-bottom: 1px solid #eee; text-align: right;">₦{pricing.get('insurance_fee', '0.00')}</td>
                </tr>
                <tr>
                    <td style="padding: 8px 0; border-bottom: 1px solid #eee;">Shipment Value:</td>
                    <td style="padding: 8px 0; border-bottom: 1px solid #eee; text-align: right;">₦{pricing.get('shipment_value', '0.00')}</td>
                </tr>
                <tr style="background: #f0f0f0; font-weight: bold; font-size: 18px;">
                    <td style="padding: 12px 8px;">TOTAL PAID:</td>
                    <td style="padding: 12px 8px; text-align: right; color: #667eea;">₦{pricing.get('total_amount', '0.00')}</td>
                </tr>
            </table>
            
            <p style="text-align: center; margin-top: 20px; color: #666; font-size: 12px;">
                This is an official receipt for your shipment.
            </p>
        </div>
        
        <p style="font-size: 16px; margin-bottom: 20px;">
            For any questions or concerns, please contact our support team with your order number.
        </p>
        
        <hr style="border: none; border-top: 1px solid #ddd; margin: 30px 0;">
        
        <p style="font-size: 14px; color: #666; text-align: center;">
            © {datetime.now().year} Transdom Express. All rights reserved.<br>
            <strong>Order #{order_no}</strong>
        </p>
    </div>
</body>
</html>
        """
        
        return self._send_email(user_email, subject, html_body)


# Create a global instance
try:
    email_service = ZohoEmailService()
except ValueError as e:
    print(f"⚠️  Email service not initialized: {str(e)}")
    email_service = None
