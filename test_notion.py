from src.notion_service import NotionClient
from config.config import NOTION_DATABASE_ID

client = NotionClient()

try:
    db = client.client.databases.retrieve(NOTION_DATABASE_ID)
    print('База данных найдена!')

    if db.get('title'):
        print('Название:', db['title'][0]['plain_text'])
except Exception as e:
    print('Ошибка:', str(e))
    print('\nВозможные причины:')
    print('1. Интеграция не добавлена к базе данных')
    print('2. Неправильный ID базы данных')
    print('3. Неправильный токен интеграции')
