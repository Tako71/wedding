# 💍 Свадебный сайт-приглашение — Артём & Яна

Одностраничный сайт-приглашение на свадьбу с формой RSVP, таймером обратного отсчёта и Telegram-уведомлениями.

**Стек:** Python 3.11 · FastAPI · SQLite · Jinja2 · Vanilla JS

---

## Быстрый старт

```bash
# 1. Клонировать репозиторий
git clone https://github.com/<your-username>/wedding.git
cd wedding

# 2. Создать виртуальное окружение
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Установить зависимости
pip install -r requirements.txt

# 4. Настроить переменные окружения
cp .env.example .env
# Заполните .env своими данными

# 5. Запустить сервер
uvicorn main:app --reload
```

Сайт доступен по адресу: http://localhost:8000

---

## Переменные окружения (`.env`)

| Переменная | Описание |
|-----------|---------|
| `TELEGRAM_BOT_TOKEN` | Токен бота из @BotFather |
| `TELEGRAM_CHAT_ID` | Ваш chat_id (получить через @userinfobot) |
| `WEDDING_DATE` | Дата свадьбы в ISO формате (`2026-09-19T12:00:00`) |
| `SECRET_ADMIN_PASSWORD` | Пароль для `/admin` страницы |
| `DATABASE_URL` | Путь к SQLite БД (по умолчанию `sqlite:///./wedding.db`) |

---

## Страницы

| URL | Описание |
|-----|---------|
| `/` | Главная страница-приглашение |
| `/rsvp` | POST — обработка формы подтверждения |
| `/thank-you` | Страница благодарности после ответа |
| `/admin` | Список всех ответов (HTTP Basic Auth) |

---

## Деплой

### Railway / Render (бесплатно)
1. Подключите GitHub-репозиторий
2. Укажите переменные окружения в настройках сервиса
3. Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

### VPS
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```
Рекомендуется настроить nginx как reverse proxy.

---

## Как получить Telegram chat_id

1. Напишите боту [@userinfobot](https://t.me/userinfobot) — он пришлёт ваш `id`
2. Создайте бота через [@BotFather](https://t.me/BotFather) и скопируйте токен
3. Напишите своему боту любое сообщение, потом откройте:  
   `https://api.telegram.org/bot<TOKEN>/getUpdates`  
   В поле `"id"` внутри `"chat"` и будет ваш chat_id