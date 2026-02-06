# Zoho Email Integration Setup Guide

This guide will help you set up Zoho email integration for sending automated emails to users during signup, order creation, and order approval.

## 📧 Email Notifications

The application now sends automated emails for:
1. **Welcome Email** - Sent when a new user signs up
2. **Order Confirmation** - Sent when a user creates a new order
3. **Order Approval/Rejection** - Sent when an admin approves or rejects an order (includes receipt)

## 🔧 Prerequisites

1. A Zoho Mail account
2. Access to Zoho Mail settings

## 📝 Step-by-Step Setup

### Step 1: Create a Zoho Mail Account

1. Go to [Zoho Mail](https://www.zoho.com/mail/)
2. Sign up for an account if you don't have one
3. Verify your email address

### Step 2: Generate Zoho App Password

For security reasons, you should use an **App-Specific Password** instead of your regular account password.

1. Log in to [Zoho Accounts](https://accounts.zoho.com/)
2. Go to **Security** → **App Passwords**
3. Click **Generate New Password**
4. Enter a name like "Transdom API Email Service"
5. Copy the generated password (you'll need this for the `.env` file)

> **Note:** If your Zoho account doesn't have 2FA enabled, you may need to enable it first to access App Passwords.

### Step 3: Configure Environment Variables

Open your `.env` file and update the Zoho email configuration:

```env
# Zoho Email Configuration
ZOHO_SMTP_SERVER=smtp.zoho.com
ZOHO_SMTP_PORT=587
ZOHO_SENDER_EMAIL=your-email@yourdomain.com
ZOHO_SENDER_PASSWORD=your-app-password-here
ZOHO_SENDER_NAME=Transdom Express
```

**Replace the following:**
- `your-email@yourdomain.com` - Your Zoho email address
- `your-app-password-here` - The app password you generated in Step 2

### Step 4: Verify Configuration

To verify your email configuration is working:

1. Start your FastAPI server:
   ```bash
   source venv/bin/activate
   uvicorn main:app --reload
   ```

2. Test the signup endpoint:
   ```bash
   curl -X POST http://localhost:8000/api/signup \
     -H "Content-Type: application/json" \
     -d '{
       "firstname": "Test",
       "lastname": "User",
       "email": "testuser@example.com",
       "password": "SecurePass123!",
       "gender": "male",
       "phone_number": "+2341234567890",
       "country": "Nigeria"
     }'
   ```

3. Check the server logs for email confirmation:
   - Success: `✓ Email sent to testuser@example.com: Welcome to Transdom Express! 🚀`
   - Failure: `✗ Failed to send email to testuser@example.com: [error message]`

4. Check the recipient's inbox for the welcome email

## 📧 Email Templates Overview

### 1. Welcome Email (Signup)
- **Trigger:** When a new user registers
- **Subject:** "Welcome to Transdom Express! 🚀"
- **Content:** Welcome message with platform features

### 2. Order Confirmation Email
- **Trigger:** When a user creates a new order
- **Subject:** "Order Confirmation - {order_no}"
- **Content:**
  - Order status (Pending Approval)
  - Order details (number, date, zone, weight)
  - Sender and receiver information
  - Pricing breakdown

### 3. Order Approval/Rejection Email
- **Trigger:** When an admin approves or rejects an order
- **Subject:** "Order Approved - {order_no} ✅" or "Order Update - {order_no}"
- **Content:**
  - Approval/rejection status
  - Complete shipment receipt
  - Order details
  - Sender and receiver information
  - Payment details
  - Cost breakdown

## 🛠️ Customization

### Updating Email Templates

Email templates are defined in [email_service.py](email_service.py). To customize:

1. Open `email_service.py`
2. Find the method for the email you want to customize:
   - `send_welcome_email()` - Welcome email
   - `send_order_confirmation_email()` - Order confirmation
   - `send_order_approval_email()` - Approval/rejection email
3. Modify the `html_body` variable with your custom HTML

### Changing Sender Information

Update these environment variables in `.env`:

```env
ZOHO_SENDER_NAME=Your Company Name
ZOHO_SENDER_EMAIL=noreply@yourcompany.com
```

## 🚨 Troubleshooting

### Email Not Sending

1. **Check SMTP credentials:**
   - Verify `ZOHO_SENDER_EMAIL` and `ZOHO_SENDER_PASSWORD` are correct
   - Ensure you're using an App Password, not your account password

2. **Check server logs:**
   - Look for error messages in the terminal where your FastAPI server is running
   - Common errors:
     - "Authentication failed" - Wrong email or password
     - "Connection refused" - Check SMTP server and port
     - "Email service not initialized" - Environment variables not set

3. **Firewall/Network Issues:**
   - Ensure port 587 (SMTP) is not blocked by your firewall
   - Try using port 465 with SSL if 587 doesn't work:
     ```env
     ZOHO_SMTP_PORT=465
     ```
   - Update `email_service.py` to use `SMTP_SSL` instead of `SMTP` with `starttls()`

4. **Test SMTP connection manually:**
   ```python
   # Run this in Python console to test SMTP
   import smtplib
   
   server = smtplib.SMTP("smtp.zoho.com", 587)
   server.starttls()
   server.login("your-email@yourdomain.com", "your-app-password")
   print("SMTP connection successful!")
   server.quit()
   ```

### Emails Going to Spam

1. **Set up SPF and DKIM records** for your domain (if using custom domain)
2. **Verify your domain** in Zoho Mail settings
3. **Add a reply-to address** in the email headers
4. **Test with different email providers** (Gmail, Outlook, etc.)

### Email Service Not Initialized

If you see this warning in logs:
```
⚠️  Email service not initialized: ZOHO_SENDER_EMAIL and ZOHO_SENDER_PASSWORD must be set in environment
```

**Solution:**
1. Make sure `.env` file exists in the project root
2. Verify the Zoho configuration variables are set in `.env`
3. Restart your FastAPI server after updating `.env`

## 📊 Monitoring Email Delivery

### Server Logs
Check your FastAPI server logs for email status:
- `✓ Email sent to user@example.com: Subject` - Success
- `✗ Failed to send email to user@example.com: Error` - Failure

### Zoho Mail Logs
1. Log in to Zoho Mail
2. Go to **Sent** folder to see sent emails
3. Check for bounce-backs in your inbox

## 🔒 Security Best Practices

1. **Never commit `.env` file** to version control (already in `.gitignore`)
2. **Use App Passwords** instead of account passwords
3. **Rotate passwords regularly**
4. **Limit SMTP access** to specific IP addresses if possible (Zoho Mail settings)
5. **Enable 2FA** on your Zoho account
6. **Monitor email sending** for unusual activity

## 🌐 Using Custom Domain

If you want to send emails from your own domain (e.g., noreply@transdom.com):

1. **Add your domain to Zoho:**
   - Go to Zoho Mail Control Panel
   - Add your domain
   - Verify ownership via DNS records

2. **Configure DNS records:**
   - Add MX records for Zoho
   - Add SPF record: `v=spf1 include:zoho.com ~all`
   - Add DKIM record (provided by Zoho)

3. **Update `.env`:**
   ```env
   ZOHO_SENDER_EMAIL=noreply@yourdomain.com
   ZOHO_SENDER_NAME=Transdom Express
   ```

## 📞 Support

If you encounter issues:
- Check [Zoho Mail Documentation](https://www.zoho.com/mail/help/)
- Review [SMTP Configuration Guide](https://www.zoho.com/mail/help/adminconsole/configure-smtp.html)
- Contact Zoho Support for account-specific issues

## ✅ Testing Checklist

- [ ] Zoho account created and verified
- [ ] App password generated
- [ ] `.env` file updated with correct credentials
- [ ] Server started successfully without initialization errors
- [ ] Welcome email received on user signup
- [ ] Order confirmation email received on order creation
- [ ] Order approval email received when admin approves order
- [ ] Emails not going to spam folder
- [ ] Email templates display correctly in different email clients

---

**Last Updated:** February 5, 2026  
**Integration Version:** 1.0.0
