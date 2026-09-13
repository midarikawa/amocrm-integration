import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # AmoCRM
    AMOCRM_SUBDOMAIN = os.getenv('AMOCRM_SUBDOMAIN')
    AMOCRM_CLIENT_ID = os.getenv('AMOCRM_CLIENT_ID')
    AMOCRM_CLIENT_SECRET = os.getenv('AMOCRM_CLIENT_SECRET')
    AMOCRM_REDIRECT_URI = os.getenv('AMOCRM_REDIRECT_URI')
    AMOCRM_ACCESS_TOKEN = os.getenv('AMOCRM_ACCESS_TOKEN')
    AMOCRM_REFRESH_TOKEN = os.getenv('AMOCRM_REFRESH_TOKEN')

    # Notion
    NOTION_TOKEN = os.getenv('NOTION_TOKEN')
    NOTION_DATABASE_ID = os.getenv('NOTION_DATABASE_ID')

    # Google Sheets
    GOOGLE_SHEETS_ID = os.getenv('GOOGLE_SHEETS_ID')
    GOOGLE_SERVICE_ACCOUNT_FILE = os.getenv('GOOGLE_SERVICE_ACCOUNT_FILE')

    # Telegram
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

    # Server
    WEBHOOK_URL = os.getenv('WEBHOOK_URL')
    PORT = int(os.getenv('PORT', 5000))
    SECRET_KEY = os.getenv('SECRET_KEY', 'change-this-secret-key')

    @staticmethod
    def validate():
        """Проверка наличия всех необходимых переменных"""
        required = [
            'AMOCRM_SUBDOMAIN',
            'AMOCRM_CLIENT_ID',
            'AMOCRM_CLIENT_SECRET',
            'NOTION_TOKEN',
            'NOTION_DATABASE_ID',
            'GOOGLE_SHEETS_ID',
            'TELEGRAM_BOT_TOKEN'
        ]

        missing = []
        for var in required:
            if not getattr(Config, var):
                missing.append(var)

        if missing:
            raise ValueError(f"Отсутствуют обязательные переменные окружения: {', '.join(missing)}")

        return True
