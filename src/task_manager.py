from sheets_service import GoogleSheetsClient
from notion_service import NotionClient
from smart_scheduler import SmartScheduler

class TaskManager:
    def __init__(self):
        self.sheets_client = GoogleSheetsClient()
        self.notion_client = NotionClient()
        self.scheduler = SmartScheduler(self.sheets_client, self.notion_client)

    def assign_task_to_specialist(self, task_data):
        """Назначить задачу подходящему специалисту"""

        specialists_count = task_data.get('specialists_count', 1)

        if specialists_count > 1:
            #Нужно несколько специалистов
            selected_specialists = self.scheduler.find_best_specialists(task_data, specialists_count)
        else:
            #Один специалист
            best_specialist = self.scheduler.find_best_specialist(task_data)
            selected_specialists = [best_specialist] if best_specialist else []

        if not selected_specialists:
            print("Не удалось найти подходящих специалистов!")
            return None

        return selected_specialists

    def create_and_assign_task(self, task_data, telegram_bot=None):
        """Создать задачу в Notion и назначить специалистов"""

        # 1. Подбираем специалистов
        specialists = self.assign_task_to_specialist(task_data)

        if not specialists:
            print("Специалисты не найдены")
            return None

        # 2. Формируем имена для записи
        specialist_names = ", ".join([s.get('Имя', '') for s in specialists])
        task_data['specialist_name'] = specialist_names

        # 3. Создаем задачу в Notion
        try:
            notion_page = self.notion_client.create_task(task_data)
            page_id = notion_page.get('id')

            print(f"Задача создана в Notion: {page_id}")
            print(f"Назначены специалисты: {specialist_names}")

            # 4. Добавляем задачу в Google Sheets для каждого специалиста
            for specialist in specialists:
                specialist_id = specialist.get('ID')
                specialist_name = specialist.get('Имя')

                self.sheets_client.add_task_to_schedule(
                    task_data,
                    specialist_id,
                    specialist_name,
                    page_id
                )

            # 5. Отправляем уведомления в Telegram
            if telegram_bot:
                for specialist in specialists:
                    telegram_id = specialist.get('Telegram ID')
                    if telegram_id:
                        #Используем asyncio для отправки
                        import asyncio
                        try:
                            asyncio.create_task(
                                telegram_bot.send_task_notification(telegram_id, task_data, page_id)
                            )
                        except Exception as e:
                            print(f"Ошибка отправки уведомления: {e}")

            return {
                'page_id': page_id,
                'specialists': specialists,
                'task_data': task_data
            }

        except Exception as e:
            print(f"Ошибка создания задачи: {e}")
            return None

    def reassign_task(self, page_id, new_specialist_id):
        """Переназначить задачу другому специалисту"""
        specialist = self.sheets_client.get_specialist_by_id(new_specialist_id)

        if not specialist:
            print(f"Специалист с ID {new_specialist_id} не найден")
            return False

        specialist_name = specialist.get('Имя', '')
        success = self.notion_client.assign_specialist(page_id, specialist_name)

        if success:
            print(f"Задача переназначена на {specialist_name}")

        return success

    def get_specialist_workload(self, specialist_id):
        """Получить загруженность специалиста (для аналитики)"""
        #В будущем можно добавить более детальную
        #статистику по задачам
        specialist = self.sheets_client.get_specialist_by_id(specialist_id)

        if not specialist:
            return None

        #Можно добавить подсчет задач из Notion
        return {
            'specialist_id': specialist_id,
            'name': specialist.get('Имя'),
            'active_tasks': 0  # TODO: добавить подсчет из Notion
        }

    def distribute_tasks_evenly(self, tasks_data_list):
        """Распределить задачи равномерно между специалистами"""
        specialists = self.sheets_client.get_active_specialists()

        if not specialists:
            print("Нет активных специалистов")
            return []

        results = []
        specialist_index = 0

        for task_data in tasks_data_list:
            #Берем следующего специалиста
            specialist = specialists[specialist_index % len(specialists)]
            task_data['specialist_name'] = specialist.get('Имя')

            #Создаем задачу
            notion_page = self.notion_client.create_task(task_data)

            results.append({
                'task': task_data,
                'specialist': specialist,
                'page_id': notion_page.get('id')
            })

            specialist_index += 1

        return results
