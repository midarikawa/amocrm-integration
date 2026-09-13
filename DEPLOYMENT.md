# 🚀 Инструкция по развертыванию системы

## 📦 Что у вас есть

Полная система интеграции AmoCRM с умным распределением задач:

- ✅ 16 файлов проекта
- ✅ Умный алгоритм распределения
- ✅ Интеграция с AmoCRM, Notion, Google Sheets, Telegram
- ✅ Полная документация

## 🎯 Пошаговый план запуска

### Этап 1: Подготовка (30 минут)

#### 1.1 Создайте аккаунты в сервисах

- [ ] AmoCRM (если еще нет)
- [ ] Notion (бесплатный план)
- [ ] Google Cloud Console (бесплатно)
- [ ] Telegram (для создания бота)

#### 1.2 Установите зависимости

```bash
cd C:\Users\Ardak\amocrm-integration
pip install -r requirements.txt
```

### Этап 2: Настройка сервисов (1-2 часа)

Следуйте инструкции в **SETUP_GUIDE.md**:

#### 2.1 AmoCRM
- [ ] Создать интеграцию
- [ ] Получить Client ID и Client Secret
- [ ] Настроить Redirect URI
- [ ] Настроить Webhook
- [ ] Создать кастомные поля в сделках

#### 2.2 Notion
- [ ] Создать интеграцию
- [ ] Получить Integration Token
- [ ] Создать базу данных "Задачи специалистов"
- [ ] Настроить поля базы данных
- [ ] Предоставить доступ интеграции

#### 2.3 Google Sheets
- [ ] Создать проект в Google Cloud
- [ ] Включить Google Sheets API
- [ ] Создать Service Account
- [ ] Скачать JSON с ключами
- [ ] Создать таблицу "Специалисты"
- [ ] Дать доступ Service Account

#### 2.4 Telegram
- [ ] Создать бота через @BotFather
- [ ] Получить Bot Token
- [ ] Сохранить username бота

### Этап 3: Конфигурация (15 минут)

#### 3.1 Создайте .env файл

```bash
copy config\.env.example config\.env
```

#### 3.2 Заполните все переменные

Откройте `config\.env` и заполните:

```env
# AmoCRM
AMOCRM_SUBDOMAIN=ваш_поддомен
AMOCRM_CLIENT_ID=ваш_client_id
AMOCRM_CLIENT_SECRET=ваш_client_secret
AMOCRM_REDIRECT_URI=http://localhost:5000/amocrm/callback
AMOCRM_ACCESS_TOKEN=
AMOCRM_REFRESH_TOKEN=

# Notion
NOTION_TOKEN=secret_ваш_токен
NOTION_DATABASE_ID=ваш_database_id

# Google Sheets
GOOGLE_SHEETS_ID=ваш_sheet_id
GOOGLE_SERVICE_ACCOUNT_FILE=config/google_credentials.json

# Telegram
TELEGRAM_BOT_TOKEN=ваш_bot_token

# Server
WEBHOOK_URL=http://localhost:5000
PORT=5000
SECRET_KEY=ваш_случайный_ключ
```

#### 3.3 Скопируйте Google credentials

Поместите скачанный JSON файл в:
```
C:\Users\Ardak\amocrm-integration\config\google_credentials.json
```

### Этап 4: Первый запуск (10 минут)

#### 4.1 Запустите сервер

```bash
python src/main.py
```

Вы должны увидеть:
```
✅ Конфигурация проверена
🤖 Инициализация Telegram бота...
🚀 Сервер запущен на порту 5000
```

#### 4.2 Получите токены AmoCRM

1. Откройте браузер: `http://localhost:5000/amocrm/auth`
2. Авторизуйтесь в AmoCRM
3. Скопируйте полученные токены
4. Вставьте их в `.env`:
   ```env
   AMOCRM_ACCESS_TOKEN=полученный_access_token
   AMOCRM_REFRESH_TOKEN=полученный_refresh_token
   ```
5. Перезапустите сервер

### Этап 5: Добавление специалистов (10 минут)

#### 5.1 Откройте Google Таблицу

Таблица должна иметь структуру:

| ID | Имя | Telegram ID | Статус | Специализация |
|----|-----|-------------|--------|---------------|

#### 5.2 Добавьте специалистов

Пример:
```
1 | Иван Иванов | 123456789 | Активен | Дезинфекция
2 | Петр Петров | 987654321 | Активен | Дератизация
3 | Сидор Сидоров | 555555555 | Активен | Дезинфекция
```

**Как узнать Telegram ID:**
1. Специалист пишет боту @userinfobot
2. Бот отвечает с его ID
3. Вносите ID в таблицу

#### 5.3 Специалисты запускают бота

Каждый специалист должен:
1. Найти вашего бота в Telegram
2. Отправить `/start`
3. Получить подтверждение:
   ```
   👋 Привет, Иван Иванов!
   Вы зарегистрированы как специалист.
   ```

### Этап 6: Тестирование (15 минут)

#### 6.1 Тест создания задачи

```bash
curl -X POST http://localhost:5000/api/test/create-task -H "Content-Type: application/json" -d "{\"address\": \"Москва, ул. Ленина, 1\", \"phone\": \"+7 999 999-99-99\", \"date\": \"2026-05-10\", \"time\": \"10:00\", \"work_type\": \"Дезинфекция\", \"pests\": \"Тараканы\", \"work_time\": 60, \"cost\": 5000}"
```

**Ожидаемый результат:**
1. ✅ Задача создана в Notion
2. ✅ Задача добавлена в Google Sheets (лист "Расписание")
3. ✅ Специалист получил уведомление в Telegram

#### 6.2 Тест команд Telegram

Специалист отправляет:
- `/schedule` - должно показать расписание на сегодня
- `/schedule_tomorrow` - расписание на завтра
- `/schedule_week` - расписание на неделю

#### 6.3 Проверьте Google Sheets

Должен автоматически создаться лист "Расписание" с задачей.

### Этап 7: Деплой на сервер (30 минут)

#### Вариант A: Render.com (рекомендуется)

1. Создайте GitHub репозиторий:
   ```bash
   cd C:\Users\Ardak\amocrm-integration
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/ваш_username/amocrm-integration.git
   git push -u origin main
   ```

2. Зарегистрируйтесь на https://render.com

3. New → Web Service

4. Подключите GitHub репозиторий

5. Настройки:
   - **Name:** amocrm-integration
   - **Environment:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python src/main.py`

6. Environment Variables:
   - Добавьте все переменные из `.env`
   - **Важно:** Измените `WEBHOOK_URL` на URL вашего Render сервиса

7. Deploy

8. После деплоя обновите Redirect URI в AmoCRM:
   ```
   https://ваш-сервис.onrender.com/amocrm/callback
   ```

9. Обновите Webhook URL в AmoCRM:
   ```
   https://ваш-сервис.onrender.com/webhook/amocrm
   ```

#### Вариант B: Railway.app

1. Зарегистрируйтесь на https://railway.app
2. New Project → Deploy from GitHub
3. Выберите репозиторий
4. Добавьте Environment Variables
5. Deploy
6. Обновите URLs в AmoCRM

### Этап 8: Финальная проверка (10 минут)

#### 8.1 Проверьте health endpoint

```bash
curl https://ваш-сервис.onrender.com/health
```

Ответ: `{"status": "ok"}`

#### 8.2 Создайте тестовую сделку в AmoCRM

1. Откройте AmoCRM
2. Создайте новую сделку
3. Заполните все поля
4. Сохраните

**Ожидаемый результат:**
- ✅ Webhook получен сервером
- ✅ Задача создана в Notion
- ✅ Задача в Google Sheets
- ✅ Уведомление в Telegram

#### 8.3 Проверьте логи

На Render.com:
- Dashboard → Logs
- Должны видеть логи обработки webhook

## 🎓 Обучение команды

### Для диспетчера

**Добавление специалиста:**
1. Откройте Google Таблицу
2. Добавьте строку с данными специалиста
3. Специалист запускает бота `/start`

**Просмотр расписания:**
1. Откройте Google Таблицу
2. Лист "Расписание"
3. Фильтруйте по дате или специалисту

**Ручное переназначение:**
```bash
curl -X POST https://ваш-сервис/api/tasks/assign \
  -H "Content-Type: application/json" \
  -d '{"page_id": "notion_page_id", "specialist_id": 2}'
```

### Для специалистов

**Основные команды:**
- `/start` - Регистрация
- `/schedule` - Расписание на сегодня
- `/schedule_tomorrow` - Расписание на завтра
- `/schedule_week` - Расписание на неделю
- `/help` - Справка

**Работа с задачами:**
1. Получаете уведомление о новой задаче
2. Нажимаете "✅ Выполнено" после завершения
3. Или "⚠️ Проблема" если что-то не так

## 🔧 Настройка алгоритма

Если нужно изменить приоритеты распределения:

Откройте `src/smart_scheduler.py`, найдите метод `calculate_specialist_score`:

```python
# Специализация (по умолчанию: 30)
if work_type.lower() in specialization.lower():
    score += 30  # ← Измените вес

# Доступность времени (по умолчанию: 40)
if not self.is_time_slot_available(...):
    score -= 40  # ← Измените штраф

# Загруженность (по умолчанию: 20)
if workload < 240:
    score += 10  # ← Измените пороги

# География (по умолчанию: 10)
if closest_distance < 10:
    score += 10  # ← Измените бонус
```

## 📊 Мониторинг

### Ежедневно проверяйте:
- [ ] Логи сервера (нет ошибок)
- [ ] Все специалисты получают уведомления
- [ ] Задачи создаются в Notion и Google Sheets
- [ ] Webhook от AmoCRM работает

### Еженедельно:
- [ ] Анализ загруженности специалистов
- [ ] Проверка качества распределения
- [ ] Обратная связь от специалистов

## 🚨 Troubleshooting

### Проблема: Специалист не получает уведомления

**Решение:**
1. Проверьте, что специалист запустил бота `/start`
2. Проверьте Telegram ID в Google Таблице
3. Проверьте логи сервера

### Проблема: Задачи не создаются в Notion

**Решение:**
1. Проверьте NOTION_TOKEN в .env
2. Проверьте, что интеграция добавлена к базе данных
3. Проверьте NOTION_DATABASE_ID

### Проблема: Ошибка Google Sheets

**Решение:**
1. Проверьте, что Service Account добавлен в таблицу
2. Проверьте путь к google_credentials.json
3. Проверьте GOOGLE_SHEETS_ID

### Проблема: Webhook не работает

**Решение:**
1. Проверьте URL webhook в AmoCRM
2. Проверьте, что сервер доступен извне
3. Проверьте логи сервера

## ✅ Чек-лист готовности

- [ ] Все зависимости установлены
- [ ] .env файл настроен
- [ ] AmoCRM интеграция создана
- [ ] Notion база данных создана
- [ ] Google Sheets настроен
- [ ] Telegram бот создан
- [ ] Специалисты добавлены в таблицу
- [ ] Специалисты запустили бота
- [ ] Тестовая задача успешно создана
- [ ] Сервер задеплоен
- [ ] Webhook настроен в AmoCRM
- [ ] Команда обучена

## 🎉 Готово!

Ваша система готова к работе. Теперь каждая новая сделка в AmoCRM будет автоматически:
1. Анализироваться умным алгоритмом
2. Назначаться лучшему специалисту
3. Добавляться в расписание
4. Отправляться в Telegram

**Следующие шаги:**
1. Мониторьте работу первые 2-3 дня
2. Собирайте обратную связь от специалистов
3. Корректируйте веса алгоритма при необходимости
4. Планируйте дальнейшие улучшения

---

**Удачи! 🚀**
