import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "dev"
    SQLALCHEMY_DATABASE_URI = (
        os.environ.get("DATABASE_URL") or "sqlite:///instance/prompts.db"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    RESEND_API_KEY = os.environ.get("RESEND_API_KEY")
