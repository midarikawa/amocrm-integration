from notion_client import Client
from datetime import datetime
from config.config import Config

class NotionClient:
    def __init__(self):
        self.client = Client(auth=Config.NOTION_TOKEN)
        self.database_id = Config.NOTION_DATABASE_ID

    def create_task(self, task_data):
        """Создать задачу в Notion"""
        properties = {
            "Адрес": {
                "title": [
                    {
                        "text": {
                            "content": task_data.get('address', 'Не указан')
                        }
                    }
                ]
            },
            "Статус": {
                "select": {
                    "name": "Назначена"
                }
            },
            "Дата визита": {
                "date": {
                    "start": task_data.get('visit_date', datetime.now().strftime('%Y-%m-%d'))
                }
            },
            "Телефон": {
                "phone_number": task_data.get('contact_phone', '')
            },
            "Email": {
                "email": task_data.get('contact_email', '')
            },
            "Описание": {
                "rich_text": [
                    {
                        "text": {
                            "content": task_data.get('description', '')
                        }
                    }
                ]
            },
            "Способ оплаты": {
                "rich_text": [
                    {
                        "text": {
                            "content": task_data.get('payment_method', '')
                        }
                    }
                ]
            },
            "Сегмент": {
                "rich_text": [
                    {
                        "text": {
                            "content": task_data.get('segment', '')
                        }
                    }
                ]
            },
            "Тип объекта": {
                "rich_text": [
                    {
                        "text": {
                            "content": task_data.get('object_type', '')
                        }
                    }
                ]
            },
            "Тип работы": {
                "rich_text": [
                    {
                        "text": {
                            "content": task_data.get('work_type', '')
                        }
                    }
                ]
            },
            "Вредители": {
                "rich_text": [
                    {
                        "text": {
                            "content": task_data.get('pests', '')
                        }
                    }
                ]
            },
            "Тип АВР": {
                "rich_text": [
                    {
                        "text": {
                            "content": task_data.get('avr_type', '')
                        }
                    }
                ]
            },
            "Количество специалистов": {
                "number": task_data.get('specialists_count', 1)
            },
            "Время работы": {
                "number": task_data.get('work_time', 0)
            },
            "Стоимость": {
                "number": task_data.get('cost', 0)
            },
            "AmoCRM ID": {
                "rich_text": [
                    {
                        "text": {
                            "content": str(task_data.get('lead_id', ''))
                        }
                    }
                ]
            }
        }

        #Добавляем специалиста, если назначен
        if task_data.get('specialist_name'):
            properties["Специалист"] = {
                "rich_text": [
                    {
                        "text": {
                            "content": task_data.get('specialist_name', '')
                        }
                    }
                ]
            }

        try:
            response = self.client.pages.create(
                parent={"database_id": self.database_id},
                properties=properties
            )
            return response
        except Exception as e:
            print(f"Ошибка создания задачи Notion: {e}")
            raise

    def update_task_status(self, page_id, status):
        """Обновить статус задачи"""
        try:
            self.client.pages.update(
                page_id=page_id,
                properties={
                    "Статус": {
                        "select": {
                            "name": status
                        }
                    }
                }
            )
            return True
        except Exception as e:
            print(f"Ошибка обновления статуса Notion: {e}")
            return False

    def assign_specialist(self, page_id, specialist_name):
        """Назначить специалиста на задачу"""
        try:
            self.client.pages.update(
                page_id=page_id,
                properties={
                    "Специалист": {
                        "rich_text": [
                            {
                                "text": {
                                    "content": specialist_name
                                }
                            }
                        ]
                    },
                    "Статус": {
                        "select": {
                            "name": "Назначена"
                        }
                    }
                }
            )
            return True
        except Exception as e:
            print(f"Ошибка назначения специалиста Notion: {e}")
            return False

    def get_task_by_lead_id(self, lead_id):
        """Найти задачу по ID сделки AmoCRM"""
        try:
            response = self.client.databases.query(
                database_id=self.database_id,
                filter={
                    "property": "AmoCRM ID",
                    "rich_text": {
                        "equals": str(lead_id)
                    }
                }
            )

            if response.get('results'):
                return response['results'][0]
            return None
        except Exception as e:
            print(f"Ошибка поиска задачи Notion: {e}")
            return None

    def add_comment(self, page_id, comment_text):
        """Добавить комментарий к задаче"""
        try:
            self.client.comments.create(
                parent={"page_id": page_id},
                rich_text=[
                    {
                        "text": {
                            "content": comment_text
                        }
                    }
                ]
            )
            return True
        except Exception as e:
            print(f"Ошибка добавления комментария Notion: {e}")
            return False

    def get_tasks_by_status(self, status):
        """Получить задачи по статусу"""
        try:
            response = self.client.databases.query(
                database_id=self.database_id,
                filter={
                    "property": "Статус",
                    "select": {
                        "equals": status
                    }
                }
            )
            return response.get('results', [])
        except Exception as e:
            print(f"Ошибка получения задач Notion: {e}")
            return []
