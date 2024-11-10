import requests

api_key = "e_RbUrqqzF_NMUorJSKLMfdukPpi9TWPvP6"
headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
data = {
    "from": "onboarding@resend.dev",
    "to": ["emeeranjp@gmail.com"],
    "subject": "Test Email",
    "html": "<p>This is a test email</p>",
}

response = requests.post("https://api.resend.com/emails", headers=headers, json=data)
print(response.status_code)
print(response.text)
