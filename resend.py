import os
import resend


class ResendClient:
    def __init__(self, api_key):
        self.api_key = api_key
        resend.api_key = api_key

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
