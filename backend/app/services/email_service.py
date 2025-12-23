import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import settings


async def send_reset_password_email(email: str, reset_token: str) -> bool:
    """
    Send reset password email to user.
    Returns True if email sent successfully, False otherwise.
    """
    try:
        # Check if email settings are configured
        if not all([
            settings.SMTP_HOST,
            settings.SMTP_USER,
            settings.SMTP_PASSWORD,
            settings.EMAILS_FROM_EMAIL
        ]):
            print(f"⚠️ Email settings not configured. Reset token: {reset_token}")
            return False
        
        # Create email message
        msg = MIMEMultipart("alternative")
        msg["Subject"] = "Reset Your Password - Insight Bridge"
        msg["From"] = f"{settings.EMAILS_FROM_NAME} <{settings.EMAILS_FROM_EMAIL}>"
        msg["To"] = email
        
        # Email body (HTML)
        html = f"""
        <html>
            <body>
                <h2>Reset Your Password</h2>
                <p>You requested to reset your password for Insight Bridge.</p>
                <p>Please use the following token to reset your password:</p>
                <p><strong>{reset_token}</strong></p>
                <p>This token will expire in 1 hour.</p>
                <p>If you did not request this, please ignore this email.</p>
                <br>
                <p>Best regards,<br>Insight Bridge Team</p>
            </body>
        </html>
        """
        
        # Email body (plain text)
        text = f"""
        Reset Your Password
        
        You requested to reset your password for Insight Bridge.
        
        Please use the following token to reset your password:
        {reset_token}
        
        This token will expire in 1 hour.
        
        If you did not request this, please ignore this email.
        
        Best regards,
        Insight Bridge Team
        """
        
        part1 = MIMEText(text, "plain")
        part2 = MIMEText(html, "html")
        msg.attach(part1)
        msg.attach(part2)
        
        # Send email via SMTP
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.send_message(msg)
        
        print(f"✅ Reset password email sent to {email}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to send email to {email}: {e}")
        print(f"⚠️ Reset token for debugging: {reset_token}")
        return False
