import os
import logging
from typing import Optional, Dict, Any
import resend


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ResendService:
    def __init__(self):
        resend.api_key = os.getenv("RESEND_API_KEY")
        self.from_email = "onboarding@resend.dev"

    def send_email(
        self, to_email: str, subject: str, html_content: str
    ) -> Optional[Dict[str, Any]]:
        try:
            params: Emails.SendParams = {
                "from": self.from_email,
                "to": [to_email],
                "subject": subject,
                "html": html_content,
            }
            response = resend.Emails.send(params)
            logger.info(f"Email sent successfully to {to_email}")
            return response
        except Exception as e:
            logger.error(f"Failed to send email: {str(e)}")
            return None

    def send_magic_link(self, email: str, token: str) -> Optional[Dict[str, Any]]:
        subject = "Your Login Link"
        html_content = f"""
        <h2>Welcome!</h2>
        <p>Click the link below to log in:</p>
        <a href="http://localhost:5000/verify/{token}"
           style="background-color: #4CAF50;
                  color: white;
                  padding: 14px 20px;
                  text-align: center;
                  text-decoration: none;
                  display: inline-block;
                  border-radius: 4px;
                  margin: 4px 2px;">
            Login Now
        </a>
        <p>This link will expire in 15 minutes.</p>
        """
        return self.send_email(email, subject, html_content)
