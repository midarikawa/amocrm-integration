from flask import Flask, request, jsonify, redirect
import asyncio
import logging
import sys
import os

#    
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src'))

from config.config import Config
from src.amocrm_service import AmoCRMClient
from src.notion_service import NotionClient
from src.sheets_service import GoogleSheetsClient
from src.telegram_service import TelegramBot
from src.task_manager import TaskManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

#  
amocrm = AmoCRMClient()
notion = NotionClient()
sheets = GoogleSheetsClient()
task_manager = TaskManager()
telegram_bot = TelegramBot()

#    event loop
loop = None

@app.route('/')
def index():
    """Главная страница"""
    return jsonify({
        'status': 'running',
        'service': 'AmoCRM Integration',
        'version': '1.0.0'
    })

@app.route('/health')
def health():
    """Проверка здоровья сервиса"""
    return jsonify({'status': 'ok'})

@app.route('/amocrm/auth')
def amocrm_auth():
    """Начать процесс авторизации AmoCRM"""
    auth_url = amocrm.get_auth_url()
    return redirect(auth_url)

@app.route('/amocrm/callback')
def amocrm_callback():
    """Callback после авторизации AmoCRM"""
    code = request.args.get('code')

    if not code:
        return jsonify({'error': 'No authorization code provided'}), 400

    try:
        tokens = amocrm.get_access_token(code)
        return jsonify({
            'success': True,
            'message': 'Авторизация успешна! Сохраните токены в .env файл',
            'access_token': tokens['access_token'],
            'refresh_token': tokens['refresh_token']
        })
    except Exception as e:
        logger.error(f"Ошибка авторизации: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/webhook/amocrm', methods=['POST'])
def amocrm_webhook():
    """Webhook для получения событий AmoCRM"""
    try:
        data = request.json
        logger.info(f"Получен webhook от AmoCRM: {data}")

        #Проверяем тип события
        if 'leads' not in data:
            return jsonify({'status': 'ignored', 'reason': 'not a lead event'}), 200

        #Обрабатываем новые сделки
        for event in data['leads']['add']:
            lead_id = event['id']
            logger.info(f"Новая сделка: {lead_id}")

            #Получаем данные из AmoCRM
            task_data = amocrm.extract_lead_data(lead_id)

            #Создаем и назначаем задачу
            result = task_manager.create_and_assign_task(task_data, telegram_bot)

            if result:
                logger.info(f"Задача успешно создана: {result['page_id']}")
            else:
                logger.error(f"Не удалось создать задачу для сделки {lead_id}")

        return jsonify({'status': 'success'}), 200

    except Exception as e:
        logger.error(f"Ошибка обработки webhook: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/specialists', methods=['GET'])
def get_specialists():
    """Получить список специалистов"""
    try:
        specialists = sheets.get_all_specialists()
        return jsonify({'specialists': specialists})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/specialists', methods=['POST'])
def add_specialist():
    """Добавить специалиста"""
    try:
        data = request.json
        name = data.get('name')
        telegram_id = data.get('telegram_id')
        specialization = data.get('specialization', '')

        if not name or not telegram_id:
            return jsonify({'error': 'Name and telegram_id are required'}), 400

        specialist_id = sheets.add_specialist(name, telegram_id, specialization)

        if specialist_id:
            return jsonify({
                'success': True,
                'specialist_id': specialist_id,
                'message': 'Специалист добавлен'
            })
        else:
            return jsonify({'error': 'Failed to add specialist'}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/specialists/<int:specialist_id>', methods=['DELETE'])
def delete_specialist(specialist_id):
    """Удалить специалиста (деактивировать)"""
    try:
        success = sheets.delete_specialist(specialist_id)

        if success:
            return jsonify({
                'success': True,
                'message': f'Специалист {specialist_id} деактивирован'
            })
        else:
            return jsonify({'error': 'Specialist not found'}), 404

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/tasks/assign', methods=['POST'])
def manual_assign_task():
    """Переназначить задачу вручную"""
    try:
        data = request.json
        page_id = data.get('page_id')
        specialist_id = data.get('specialist_id')

        if not page_id or not specialist_id:
            return jsonify({'error': 'page_id and specialist_id are required'}), 400

        success = task_manager.reassign_task(page_id, specialist_id)

        if success:
            return jsonify({
                'success': True,
                'message': 'Задача переназначена'
            })
        else:
            return jsonify({'error': 'Failed to reassign task'}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/test/create-task', methods=['POST'])
def test_create_task():
    """Тестовый endpoint для создания задачи"""
    try:
        data = request.json

        #Формируем данные задачи
        task_data = {
            'lead_id': data.get('lead_id', 'TEST-001'),
            'address': data.get('address', 'Тестовый адрес'),
            'contact_phone': data.get('phone', '+7 999 999-99-99'),
            'contact_email': data.get('email', 'test@example.com'),
            'visit_date': data.get('date', '2026-05-10'),
            'visit_time': data.get('time', '10:00'),
            'description': data.get('description', 'Тестовая задача'),
            'payment_method': data.get('payment_method', 'Наличные'),
            'segment': data.get('segment', 'B2C'),
            'object_type': data.get('object_type', 'Квартира'),
            'work_type': data.get('work_type', 'Дезинфекция'),
            'pests': data.get('pests', 'Тараканы'),
            'avr_type': data.get('avr_type', 'Плановая'),
            'specialists_count': int(data.get('specialists_count', 1)),
            'work_time': int(data.get('work_time', 60)),
            'cost': float(data.get('cost', 5000))
        }

        result = task_manager.create_and_assign_task(task_data, telegram_bot)

        if result:
            return jsonify({
                'success': True,
                'page_id': result['page_id'],
                'specialists': [s.get('Имя') for s in result['specialists']]
            })
        else:
            return jsonify({'error': 'Failed to create task'}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500

async def init_telegram_bot():
    """Инициализация Telegram бота"""
    global telegram_bot
    await telegram_bot.initialize()

def run_flask():
    """Запуск Flask сервера"""
    port = Config.PORT
    logger.info(f"Запуск Flask сервера на порту {port}")
    app.run(host='0.0.0.0', port=port, debug=False)

if __name__ == '__main__':
    try:
        #Валидация конфигурации
        Config.validate()
        logger.info("Конфигурация валидна")

        #Инициализация Telegram бота
        logger.info("Инициализация Telegram бота...")
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(init_telegram_bot())

        #Запуск Flask сервера
        run_flask()

    except Exception as e:
        logger.error(f"Ошибка запуска: {e}")
        raise
