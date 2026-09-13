from src.notion_service import NotionClient
import json

client = NotionClient()

print('Поиск всех баз данных, доступных интеграции...\n')

try:
    # Получаем список всех страниц
    response = client.client.search(filter={"property": "object", "value": "database"})

    if response['results']:
        print(f'Найдено баз данных: {len(response["results"])}\n')
        for db in response['results']:
            db_id = db['id']
            title = db.get('title', [{}])[0].get('plain_text', 'Без названия') if db.get('title') else 'Без названия'
            print(f'База данных: {title}')
            print(f'ID: {db_id}')
            print(f'URL: https://www.notion.so/{db_id.replace("-", "")}')
            print()
    else:
        print('Не найдено ни одной базы данных.')
        print('\nВозможные причины:')
        print('1. Вы не добавили интеграцию ни к одной базе данных')
        print('2. Вы создали страницу, а не базу данных')

except Exception as e:
    print('Ошибка:', str(e))
