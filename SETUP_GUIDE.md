# Инструкция по настройке интеграции AmoCRM

## 📋 Шаг 1: Настройка AmoCRM

### 1.1 Создание интеграции

1. Войдите в AmoCRM
2. Перейдите в **Настройки** → **Интеграции** → **Создать интеграцию**
3. Заполните данные:
   - Название: "Система управления специалистами"
   - Redirect URI: `https://your-domain.com/amocrm/callback`
4. Сохраните **Client ID** и **Client Secret**

### 1.2 Настройка Webhook

1. В настройках интеграции включите **Webhooks**
2. Добавьте URL: `https://your-domain.com/webhook/amocrm`
3. Выберите события:
   - ✅ Добавление сделки
   - ✅ Изменение сделки

### 1.3 Настройка кастомных полей в сделках

Создайте следующие поля в сделках (Настройки → Поля → Сделки):

- **Адрес** (текст)
- **Дата визита** (дата)
- **Время визита** (текст)
- **Метод оплаты** (список)
- **Сегмент** (список)
- **Вид объекта** (список)
- **Вид работ** (список)
- **Вредители** (список)
- **Вид АВР** (текст)
- **Количество спец** (число)
- **Время на работу (мин)** (число)
- **Стоимость** (число)

---

## 📊 Шаг 2: Настройка Notion

### 2.1 Создание интеграции

1. Перейдите на https://www.notion.so/my-integrations
2. Нажмите **+ New integration**
3. Заполните:
   - Name: "AmoCRM Integration"
   - Associated workspace: выберите ваш workspace
4. Скопируйте **Internal Integration Token**

### 2.2 Создание базы данных

1. Создайте новую страницу в Notion
2. Добавьте **Database - Table**
3. Назовите: "Задачи специалистов"

### 2.3 Настройка полей базы данных

Создайте следующие свойства (Properties):

| Название | Тип | Описание |
|----------|-----|----------|
| Название | Title | Адрес клиента |
| Статус | Select | Новая, Назначена, В работе, Выполнена, Проблема |
| Специалист | Text | Имя специалиста |
| Дата визита | Date | Дата |
| Телефон | Phone | Телефон клиента |
| Email | Email | Email клиента |
| Описание | Text | Описание задачи |
| Метод оплаты | Text | Способ оплаты |
| Сегмент | Text | Сегмент клиента |
| Вид объекта | Text | Тип объекта |
| Вид работ | Text | Вид работ |
| Вредители | Text | Вредители |
| Вид АВР | Text | Вид АВР |
| Количество спец | Number | Количество специалистов |
| Время на работу | Number | Минуты |
| Стоимость | Number | Рубли |
| AmoCRM ID | Text | ID сделки |

### 2.4 Предоставление доступа

1. Откройте созданную базу данных
2. Нажмите **Share** (вверху справа)
3. Найдите вашу интеграцию и добавьте её
4. Скопируйте **Database ID** из URL:
   - URL: `https://notion.so/workspace/DATABASE_ID?v=...`

---

## 📝 Шаг 3: Настройка Google Sheets

### 3.1 Создание проекта в Google Cloud

1. Перейдите на https://console.cloud.google.com/
2. Создайте новый проект
3. Включите **Google Sheets API**:
   - APIs & Services → Enable APIs and Services
   - Найдите "Google Sheets API" → Enable

### 3.2 Создание Service Account

1. APIs & Services → Credentials
2. Create Credentials → Service Account
3. Заполните данные и создайте
4. Нажмите на созданный Service Account
5. Keys → Add Key → Create New Key → JSON
6. Скачайте JSON файл и сохраните как `config/google_credentials.json`

### 3.3 Создание таблицы специалистов

1. Создайте новую Google Таблицу
2. Назовите: "Специалисты"
3. Создайте заголовки в первой строке:

| ID | Имя | Telegram ID | Статус | Специализация |
|----|-----|-------------|--------|---------------|

4. Нажмите **Share** и добавьте email Service Account (из JSON файла)
5. Скопируйте **Sheet ID** из URL:
   - URL: `https://docs.google.com/spreadsheets/d/SHEET_ID/edit`

---

## 🤖 Шаг 4: Создание Telegram бота

1. Найдите @BotFather в Telegram
2. Отправьте `/newbot`
3. Придумайте имя: "Специалисты Бот"
4. Придумайте username: `specialists_bot`
5. Скопируйте **Bot Token**

---

## ⚙️ Шаг 5: Настройка проекта

### 5.1 Установка зависимостей

```bash
cd amocrm-integration
pip install -r requirements.txt
```

### 5.2 Создание .env файла

Скопируйте `.env.example` в `.env`:

```bash
copy config\.env.example .env
```

Заполните все переменные:

```env
# AmoCRM
AMOCRM_SUBDOMAIN=your_subdomain
AMOCRM_CLIENT_ID=your_client_id
AMOCRM_CLIENT_SECRET=your_client_secret
AMOCRM_REDIRECT_URI=https://your-domain.com/amocrm/callback
AMOCRM_ACCESS_TOKEN=
AMOCRM_REFRESH_TOKEN=

# Notion
NOTION_TOKEN=secret_xxxxxxxxxxxxx
NOTION_DATABASE_ID=xxxxxxxxxxxxx

# Google Sheets
GOOGLE_SHEETS_ID=xxxxxxxxxxxxx
GOOGLE_SERVICE_ACCOUNT_FILE=config/google_credentials.json

# Telegram
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz

# Server
WEBHOOK_URL=https://your-domain.com
PORT=5000
SECRET_KEY=your_random_secret_key
```

### 5.3 Получение токенов AmoCRM

1. Запустите сервер локально:
```bash
python src/main.py
```

2. Откройте в браузере:
```
http://localhost:5000/amocrm/auth
```

3. Авторизуйтесь в AmoCRM
4. Скопируйте полученные токены в `.env`

---

## 🚀 Шаг 6: Деплой на сервер

### Вариант 1: Render.com (бесплатно)

1. Зарегистрируйтесь на https://render.com
2. New → Web Service
3. Подключите GitHub репозиторий
4. Настройки:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python src/main.py`
5. Добавьте Environment Variables из `.env`
6. Deploy

### Вариант 2: Railway.app (бесплатно)

1. Зарегистрируйтесь на https://railway.app
2. New Project → Deploy from GitHub
3. Выберите репозиторий
4. Добавьте переменные окружения
5. Deploy

---

## ✅ Шаг 7: Тестирование

### 7.1 Добавление специалиста

1. Откройте Google Таблицу
2. Добавьте строку:
   - ID: 1
   - Имя: Иван Иванов
   - Telegram ID: ваш_telegram_id
   - Статус: Активен
   - Специализация: Дезинфекция

### 7.2 Тест Telegram бота

1. Найдите вашего бота в Telegram
2. Отправьте `/start`
3. Должно прийти приветствие с вашим именем

### 7.3 Тест создания задачи

Отправьте POST запрос на `/api/test/create-task`:

```bash
curl -X POST https://your-domain.com/api/test/create-task \
  -H "Content-Type: application/json" \
  -d '{
    "address": "Москва, ул. Ленина, 1",
    "phone": "+7 999 999-99-99",
    "date": "2026-05-10",
    "time": "10:00",
    "work_type": "Дезинфекция",
    "pests": "Тараканы",
    "cost": 5000
  }'
```

Должно произойти:
1. ✅ Задача создана в Notion
2. ✅ Назначен специалист
3. ✅ Уведомление отправлено в Telegram

---

## 🔧 Troubleshooting

### Ошибка: "No module named 'notion_client'"
```bash
pip install notion-client
```

### Ошибка: "Invalid Notion token"
- Проверьте токен в `.env`
- Убедитесь, что интеграция добавлена к базе данных

### Ошибка: "Google Sheets permission denied"
- Проверьте, что Service Account добавлен в таблицу
- Проверьте путь к `google_credentials.json`

### Telegram бот не отвечает
- Проверьте токен бота
- Убедитесь, что сервер запущен

---

## 📞 Поддержка

При возникновении проблем проверьте логи:
```bash
python src/main.py
```

Все ошибки будут выведены в консоль.
