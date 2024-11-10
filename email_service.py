from resend_service import ResendService
from itsdangerous import URLSafeTimedSerializer
from flask import url_for


class EmailService:
    def __init__(self, api_key=None, secret_key=None):
        self.client = ResendService(api_key)
        self.serializer = URLSafeTimedSerializer(secret_key)

    def send_welcome_email(self, to_email, username):
        subject = "Welcome to Prompt Saver!"
        html_content = f"""
        <h1>Welcome to Prompt Saver, {username}!</h1>
        <p>Thank you for joining our platform. Start saving your prompts today!</p>
        """
        return self.client.send_email(
            from_email="meeran@dev.ashiknesin.com",
            to_email=to_email,
            subject=subject,
            html_content=html_content,
        )

    def send_magic_link(self, email, base_url):
        # Generate token
        token = self.serializer.dumps(email, salt="email-confirm")

        # Create magic link
        magic_link = f"{base_url}/login/verify/{token}"

        subject = "Your Magic Login Link"
        html_content = f"""
        <h1>Login to Prompt Saver</h1>
        <p>Click the link below to log in to your account:</p>
        <a href="{magic_link}">Click here to login</a>
        <p>This link will expire in 10 minutes.</p>
        <p>If you didn't request this link, please ignore this email.</p>
        """

        return self.client.send_email(
            from_email="meeran@dev.ashiknesin.com",
            to_email=email,
            subject=subject,
            html_content=html_content,
        )
