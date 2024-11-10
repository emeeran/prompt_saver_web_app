import resend
from config import Config


class ResendService:
    def __init__(self, api_key=None):
        self.api_key = api_key or Config.RESEND_API_KEY
        resend.api_key = self.api_key

    def send_email(self, from_email, to_email, subject, html_content):
        try:
            params = {
                "from": from_email,
                "to": to_email,
                "subject": subject,
                "html": html_content,
            }
            response = resend.Emails.send(params)
            return response
        except Exception as e:
            print(f"Error sending email: {str(e)}")
            return None
