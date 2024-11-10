from resend_service import ResendService


class EmailService:
    def __init__(self, api_key=None):
        self.client = ResendService(api_key)

    def send_welcome_email(self, to_email, username):
        subject = "Welcome to Prompt Saver!"
        html_content = f"""
        <h1>Welcome to Prompt Saver, {username}!</h1>
        <p>Thank you for joining our platform. Start saving your prompts today!</p>
        """
        return self.client.send_email(
            from_email="noreply@promptsaver.com",
            to_email=to_email,
            subject=subject,
            html_content=html_content,
        )
