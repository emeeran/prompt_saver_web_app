import os
import requests
import logging
from typing import Optional
from resend_service import Resend

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ResendService:
    def __init__(self):
        self.api_key = os.getenv("RESEND_API_KEY")
        self.client = Resend(api_key=self.api_key)
        self.from_email = "onboarding@resend.dev"

    def send_email(self, to_email, subject, html_content):
        try:
            response = self.client.emails.send(
                {
                    "from": self.from_email,
                    "to": to_email,
                    "subject": subject,
                    "html": html_content,
                }
            )
            return response
        except Exception as e:
            print(f"Failed to send email: {str(e)}")
            return None

    def send_magic_link(self, email, token):
        subject = "Your Login Link"
        html_content = f"""
        <h1>Welcome!</h1>
        <p>Click the link below to log in:</p>
        <a href="http://localhost:5000/verify/{token}">Login Now</a>
        <p>This link will expire in 15 minutes.</p>
        """
        return self.send_email(email, subject, html_content)


class EmailService:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.resend.com/emails"

    def send_email(self, to_email: str, magic_link: str) -> Optional[bool]:
        if not self.api_key:
            logger.error("No API key provided")
            return None

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        data = {
            "from": "emeeran@dev.ashiknesin.com",
            "to": [to_email],
            "subject": "Your Login Link",
            "html": f"""
                <h2>Welcome to Prompt Saver</h2>
                <p>Click the button below to log in:</p>
                <a href="{magic_link}"
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
                <p>Or copy and paste this link in your browser:</p>
                <p>{magic_link}</p>
                <p>This link will expire in 15 minutes.</p>
            """,
        }

        try:
            logger.info(f"Attempting to send email to {to_email}")
            logger.debug(f"Using API key: {self.api_key[:8]}...")

            response = requests.post(self.base_url, headers=headers, json=data)

            logger.info(f"Response status: {response.status_code}")
            logger.info(f"Response body: {response.text}")

            if response.status_code == 403:
                logger.error("Authentication failed. Please check your API key.")
                return False

            response.raise_for_status()
            return True

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to send email: {str(e)}")
            if hasattr(e, "response") and e.response is not None:
                logger.error(f"Response text: {e.response.text}")
            return False
