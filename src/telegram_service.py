import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from config.config import Config
from sheets_service import GoogleSheetsClient
from notion_service import NotionClient
from amocrm_service import AmoCRMClient

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

class TelegramBot:
    def __init__(self):
        self.token = Config.TELEGRAM_BOT_TOKEN
        self.sheets_client = GoogleSheetsClient()
        self.notion_client = NotionClient()
        self.amocrm_client = AmoCRMClient()
        self.application = None

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /start"""
        telegram_id = update.effective_user.id
        specialist = self.sheets_client.get_specialist_by_telegram_id(telegram_id)

        if specialist:
            await update.message.reply_text(
                f"Привет, {specialist.get('Имя')}!\n\n"
                f"Вы успешно авторизованы в системе.\n"
                f"Специализация: {specialist.get('Специализация')}\n"
                f"Статус: {specialist.get('Статус')}\n\n"
                f"Используйте команду /help для списка доступных команд."
            )
        else:
            await update.message.reply_text(
                "Добро пожаловать!\n\n"
                "Вы еще не зарегистрированы в системе.\n"
                "Пожалуйста, передайте ваш Telegram ID администратору для регистрации.\n\n"
                f"Ваш Telegram ID: `{telegram_id}`",
                parse_mode='Markdown'
            )

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /help"""
        help_text = """
📋 *Доступные команды:*

/start - Начать работу с ботом
/help - Показать это сообщение
/schedule - Показать расписание на сегодня
/schedule_tomorrow - Расписание на завтра
/schedule_week - Расписание на неделю
/stats - Статистика работы

*Как работать с задачами:*
1. Получите уведомление о новой задаче
2. Нажмите кнопку после выполнения
3. Система автоматически обновит статус
        """
        await update.message.reply_text(help_text, parse_mode='Markdown')

    async def my_tasks(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показать активные задачи специалиста"""
        telegram_id = update.effective_user.id
        specialist = self.sheets_client.get_specialist_by_telegram_id(telegram_id)

        if not specialist:
            await update.message.reply_text("Вы не зарегистрированы в системе.")
            return

        #Получаем расписание специалиста
        specialist_id = specialist.get('ID')
        schedule = self.sheets_client.get_specialist_schedule(specialist_id)

        if not schedule:
            await update.message.reply_text("У вас пока нет задач в расписании.")
            return

        #Фильтруем только активные задачи
        active_tasks = [t for t in schedule if t.get('Статус') in ['Назначена', 'В работе']]

        if not active_tasks:
            await update.message.reply_text("У вас нет активных задач.")
            return

        message = "📋 *Ваши активные задачи:*\n\n"
        for task in active_tasks:
            message += (
                f"🎯 *Задача #{task.get('ID задачи')}*\n"
                f"📅 {task.get('Дата')} в {task.get('Время')}\n"
                f"📍 {task.get('Адрес')}\n"
                f"🔧 {task.get('Тип работы')}\n"
                f"⏱ {task.get('Время работы (мин)')} мин\n"
                f"💰 {task.get('Стоимость')} тг\n\n"
            )

        await update.message.reply_text(message, parse_mode='Markdown')

    async def schedule_today(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Расписание на сегодня"""
        from datetime import datetime
        today = datetime.now().strftime('%Y-%m-%d')
        await self._send_schedule(update, today, "сегодня")

    async def schedule_tomorrow(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Расписание на завтра"""
        from datetime import datetime, timedelta
        tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        await self._send_schedule(update, tomorrow, "завтра")

    async def schedule_week(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Расписание на неделю"""
        from datetime import datetime, timedelta
        telegram_id = update.effective_user.id
        specialist = self.sheets_client.get_specialist_by_telegram_id(telegram_id)

        if not specialist:
            await update.message.reply_text("Вы не зарегистрированы в системе.")
            return

        specialist_id = specialist.get('ID')
        message = "📅 *Расписание на неделю:*\n\n"

        for i in range(7):
            date = (datetime.now() + timedelta(days=i)).strftime('%Y-%m-%d')
            schedule = self.sheets_client.get_specialist_schedule(specialist_id, date)

            if schedule:
                day_name = (datetime.now() + timedelta(days=i)).strftime('%A, %d.%m')
                message += f"*{day_name}*\n"

                for task in sorted(schedule, key=lambda x: x.get('Время', '')):
                    message += (
                        f"  ⏰ {task.get('Время')} - {task.get('Адрес')}\n"
                        f"     {task.get('Тип работы')} ({task.get('Время работы (мин)')} мин)\n"
                    )
                message += "\n"

        if message == "📅 *Расписание на неделю:*\n\n":
            message = "На ближайшую неделю задач пока нет."

        await update.message.reply_text(message, parse_mode='Markdown')

    async def _send_schedule(self, update: Update, date: str, date_label: str):
        """Отправить расписание на конкретную дату"""
        telegram_id = update.effective_user.id
        specialist = self.sheets_client.get_specialist_by_telegram_id(telegram_id)

        if not specialist:
            await update.message.reply_text("Вы не зарегистрированы в системе.")
            return

        specialist_id = specialist.get('ID')
        schedule = self.sheets_client.get_specialist_schedule(specialist_id, date)

        if not schedule:
            await update.message.reply_text(f"На {date_label} задач пока нет.")
            return

        #Сортируем по времени
        schedule = sorted(schedule, key=lambda x: x.get('Время', ''))

        message = f"📅 *Расписание на {date_label}:*\n\n"

        total_time = 0
        total_cost = 0

        for idx, task in enumerate(schedule, 1):
            work_time = task.get('Время работы (мин)', 0)
            cost = task.get('Стоимость', 0)
            total_time += work_time
            total_cost += cost

            message += (
                f"*{idx}. {task.get('Время')}* - {task.get('Адрес')}\n"
                f"  📞 {task.get('Телефон клиента')}\n"
                f"  🔧 {task.get('Тип работы', 'Не указан')}\n"
                f"  🐛 {task.get('Вредители')}\n"
                f"  ⏱ {work_time} мин | 💰 {cost} тг\n"
                f"  📝 {task.get('Описание', 'Нет описания')[:50]}...\n\n"
            )

        message += f"\n"
        message += f"📊 *Итого:* {len(schedule)} задач(и)\n"
        message += f"⏱ *Время работы:* {total_time} мин ({total_time // 60}ч {total_time % 60}м)\n"
        message += f"💰 *Сумма:* {total_cost} тг"

        await update.message.reply_text(message, parse_mode='Markdown')

    async def send_task_notification(self, telegram_id, task_data, page_id):
        """Отправить уведомление о новой задаче"""
        message = (
            f"🎯 *Новая задача!*\n\n"
            f"📍 *Адрес:* {task_data.get('address', 'Не указан')}\n"
            f"📅 *Дата:* {task_data.get('visit_date', 'Не указана')}\n"
            f"⏰ *Время:* {task_data.get('visit_time', 'Не указано')}\n"
            f"📞 *Телефон:* {task_data.get('contact_phone', 'Не указан')}\n"
            f"🔧 *Тип работы:* {task_data.get('work_type', 'Не указан')}\n"
            f"🐛 *Вредители:* {task_data.get('pests', 'Не указаны')}\n"
            f"⏱ *Время работы:* {task_data.get('work_time', 0)} мин\n"
            f"💰 *Стоимость:* {task_data.get('cost', 0)} тг\n\n"
            f"📝 *Описание:*\n{task_data.get('description', 'Нет описания')}"
        )

        keyboard = [
            [
                InlineKeyboardButton("✅ Выполнено", callback_data=f"complete_{page_id}"),
                InlineKeyboardButton("⚠️ Проблема", callback_data=f"problem_{page_id}")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        try:
            await self.application.bot.send_message(
                chat_id=telegram_id,
                text=message,
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
            logger.info(f"Уведомление отправлено специалисту {telegram_id}")
            return True
        except Exception as e:
            logger.error(f"Ошибка отправки уведомления: {e}")
            return False

    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик нажатий на кнопки"""
        query = update.callback_query
        await query.answer()

        telegram_id = update.effective_user.id
        specialist = self.sheets_client.get_specialist_by_telegram_id(telegram_id)

        if not specialist:
            await query.edit_message_text("Вы не зарегистрированы в системе.")
            return

        data = query.data
        action, page_id = data.split('_', 1)

        if action == "complete":
            #Обновляем статус в Notion
            self.notion_client.update_task_status(page_id, "Выполнена")

            #Добавляем комментарий
            comment = f"Задача выполнена специалистом {specialist.get('Имя')}"
            self.notion_client.add_comment(page_id, comment)

            #Добавляем заметку в AmoCRM (если нужно)
            # task = self.notion_client.get_task_by_lead_id(lead_id)
            # self.amocrm_client.add_note_to_lead(lead_id, comment)

            await query.edit_message_text(
                f"{query.message.text}\n\n"
                f"✅ *Статус: Выполнена*",
                parse_mode='Markdown'
            )

        elif action == "problem":
            #Обновляем статус в Notion
            self.notion_client.update_task_status(page_id, "Проблема")

            #Добавляем комментарий
            comment = f"Специалист {specialist.get('Имя')} сообщил о проблеме"
            self.notion_client.add_comment(page_id, comment)

            await query.edit_message_text(
                f"{query.message.text}\n\n"
                f"⚠️ *Статус: Проблема*\n"
                f"Менеджер свяжется с вами для уточнения деталей.",
                parse_mode='Markdown'
            )

            #Уведомляем менеджера (опционально)
            # await self.notify_manager(page_id, specialist)

    def setup_handlers(self):
        """Регистрация обработчиков команд"""
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("tasks", self.my_tasks))
        self.application.add_handler(CommandHandler("schedule", self.schedule_today))
        self.application.add_handler(CommandHandler("schedule_tomorrow", self.schedule_tomorrow))
        self.application.add_handler(CommandHandler("schedule_week", self.schedule_week))
        self.application.add_handler(CallbackQueryHandler(self.button_callback))

    def run(self):
        """Запуск бота"""
        self.application = Application.builder().token(self.token).build()
        self.setup_handlers()

        logger.info("Telegram бот запущен!")
        self.application.run_polling(allowed_updates=Update.ALL_TYPES)

    async def initialize(self):
        """Инициализация бота для Flask"""
        self.application = Application.builder().token(self.token).build()
        self.setup_handlers()
        await self.application.initialize()
        await self.application.start()
        logger.info("Telegram бот инициализирован!")

if __name__ == '__main__':
    bot = TelegramBot()
    bot.run()
