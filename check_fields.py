from src.notion_service import NotionClient
from config.config import NOTION_DATABASE_ID
import json

client = NotionClient()

try:
    db = client.client.databases.retrieve(NOTION_DATABASE_ID)
    print('Поля в базе данных:')
    for prop_name, prop_data in db['properties'].items():
        print(f'  - {prop_name} ({prop_data["type"]})')
except Exception as e:
    print('Ошибка:', str(e))

