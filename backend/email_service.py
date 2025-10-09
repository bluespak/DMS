import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import settings
import logging

logger = logging.getLogger(__name__)


async def send_email(to_email: str, subject: str, body: str):
    """Send an email using SMTP"""
    if not settings.SMTP_USER or not settings.SMTP_PASSWORD:
        logger.warning("SMTP credentials not configured. Email not sent.")
        return False
    
    try:
        message = MIMEMultipart()
        message["From"] = settings.SMTP_FROM
        message["To"] = to_email
        message["Subject"] = subject
        
        message.attach(MIMEText(body, "plain"))
        
        await aiosmtplib.send(
            message,
            hostname=settings.SMTP_HOST,
            port=settings.SMTP_PORT,
            username=settings.SMTP_USER,
            password=settings.SMTP_PASSWORD,
            start_tls=True,
        )
        logger.info(f"Email sent successfully to {to_email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {str(e)}")
        return False
