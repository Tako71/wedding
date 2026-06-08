# 💍 Свадебный сайт-приглашение — Артём & Яна

Одностраничный сайт-приглашение на свадьбу с формой RSVP, фотогалереей, таймером обратного отсчёта и Telegram-уведомлениями.

**Стек:** Python 3.11 · FastAPI · SQLite · Jinja2 · Vanilla JS · Docker · Nginx · Let's Encrypt

**Живой сайт:** [piletskigroup.ru](https://piletskigroup.ru)

---

## Содержание

- [Архитектура](#архитектура)
- [Локальная разработка](#локальная-разработка)
- [Переменные окружения](#переменные-окружения)
- [Деплой на VPS](#деплой-на-vps)
- [Путь деплоя](#путь-деплоя)
- [Полезные команды](#полезные-команды)
- [Настройка Telegram-бота](#настройка-telegram-бота)

---

## Архитектура

```
Браузер гостя
     │
     │ HTTPS :443
     ▼
┌─────────────────────────────────────┐
│            Nginx (Docker)            │
│                                     │
│  /static/*  ──► файлы с диска       │  ◄── без Python, быстро
│  /*         ──► proxy_pass          │
└──────────────────┬──────────────────┘
                   │ HTTP :8000
                   ▼
┌─────────────────────────────────────┐
│         FastAPI + Uvicorn (Docker)   │
│                                     │
│  GET  /           → index.html      │
│  POST /rsvp       → сохранить в БД  │
│  GET  /thank-you  → страница ответа │
│  GET  /admin      → список гостей   │
│  GET  /calendar.ics → файл для кал. │
└──────────────────┬──────────────────┘
                   │
                   ▼
            SQLite (./data/wedding.db)
            Docker volume: db_data
```

Статика (CSS, JS, картинки) раздаётся напрямую Nginx — Python её не видит.  
База данных хранится в Docker volume и не теряется при пересборке контейнера.

---

## Локальная разработка

```bash
# 1. Клонировать репозиторий
git clone https://github.com/Tako71/wedding.git
cd wedding

# 2. Создать виртуальное окружение
python -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate

# 3. Установить зависимости
pip install -r requirements.txt

# 4. Настроить переменные окружения
cp .env.example .env
# Откройте .env и заполните своими данными

# 5. Запустить сервер
uvicorn main:app --reload
```

Сайт откроется по адресу: **http://localhost:8000**

> При первом запуске FastAPI автоматически создаёт файл базы данных `./data/wedding.db`.

---

## Переменные окружения (`.env`)

| Переменная | Описание | Пример |
|-----------|---------|--------|
| `TELEGRAM_BOT_TOKEN` | Токен бота из @BotFather | `1234567890:AAF...` |
| `TELEGRAM_CHAT_ID` | Ваш личный chat_id | `571682214` |
| `WEDDING_DATE` | Дата свадьбы в ISO формате | `2026-09-19T12:00:00` |
| `SECRET_ADMIN_PASSWORD` | Пароль для страницы `/admin` | `my-secret-pass` |
| `DATABASE_URL` | Путь к SQLite БД | `sqlite:///./data/wedding.db` |

---

## Деплой на VPS

### Требования к серверу

- Ubuntu 20.04 / 22.04
- Минимум 1 CPU, 1 GB RAM, 10 GB диск
- Открытые порты: 80, 443
- Доменное имя с A-записью, указывающей на IP сервера

### Шаг 1 — Установка Docker

```bash
apt-get update -y
apt-get install -y ca-certificates curl gnupg

install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg \
  | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
chmod a+r /etc/apt/keyrings/docker.gpg

echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
  https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo $VERSION_CODENAME) stable" \
  > /etc/apt/sources.list.d/docker.list

apt-get update -y
apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
```

### Шаг 2 — Клонировать репозиторий

```bash
git clone https://github.com/Tako71/wedding.git /opt/wedding
cd /opt/wedding
```

### Шаг 3 — Настроить окружение

```bash
cp .env.example .env
nano .env   # заполнить все переменные
```

> `DATABASE_URL` на сервере должен быть `sqlite:////app/data/wedding.db` (абсолютный путь внутри контейнера).

### Шаг 4 — Прописать домен в nginx.conf

```bash
sed -i 's/YOUR_DOMAIN/ваш-домен.ru/g' nginx.conf
```

### Шаг 5 — Получить SSL-сертификат (Let's Encrypt)

```bash
# Запустить только nginx для прохождения HTTP-верификации
docker compose up -d nginx

# Установить certbot и получить сертификат
apt-get install -y certbot
certbot certonly --standalone \
  --email you@email.com \
  --agree-tos \
  --no-eff-email \
  -d ваш-домен.ru \
  -d www.ваш-домен.ru
```

> Сертификат сохраняется в `/etc/letsencrypt/live/ваш-домен.ru/`.

### Шаг 6 — Запустить все сервисы

```bash
docker compose up -d --build
```

Сайт будет доступен по `https://ваш-домен.ru`.

---

## Путь деплоя

Так выглядит процесс от правки кода до появления изменений на сайте:

```
Локальная машина
    │
    │  1. Вносим правки в код
    │  2. git add . && git commit -m "..."
    │  3. git push origin main
    ▼
GitHub (Tako71/wedding)
    │
    │  4. git pull origin main  (на сервере)
    ▼
VPS /opt/wedding/
    │
    ├─ Изменился Python-код или шаблоны?
    │       docker compose up -d --build app
    │
    ├─ Изменился CSS / JS / картинки?
    │       ничего — nginx видит новые файлы сразу после git pull
    │       (только поднять версию ?v=N в index.html чтобы сбросить кэш браузера)
    │
    └─ Изменился nginx.conf?
            git pull → sed (домен) → docker compose restart nginx
```

### Что кто раздаёт

| Запрос | Обрабатывает |
|--------|-------------|
| `GET /` — HTML страница | Nginx → проксирует в FastAPI |
| `POST /rsvp` — форма | Nginx → FastAPI → SQLite + Telegram |
| `GET /static/css/style.css` | **Nginx напрямую** с диска |
| `GET /static/js/main.js` | **Nginx напрямую** с диска |
| `GET /static/images/*` | **Nginx напрямую** с диска |

---

## Полезные команды

```bash
# Посмотреть запущенные контейнеры
docker compose ps

# Логи FastAPI в реальном времени
docker compose logs -f app

# Логи Nginx
docker compose logs -f nginx

# Перезапустить только приложение
docker compose restart app

# Полная пересборка и перезапуск
docker compose up -d --build

# Остановить всё
docker compose down

# Зайти внутрь контейнера
docker compose exec app bash

# Посмотреть базу данных
docker compose exec app python -c "
from database import SessionLocal
from models import RSVP
db = SessionLocal()
for r in db.query(RSVP).all():
    print(r.name, r.attending)
"
```

---

## Настройка Telegram-бота

1. Создайте бота через [@BotFather](https://t.me/BotFather) → скопируйте токен
2. Напишите боту любое сообщение
3. Откройте в браузере:
   ```
   https://api.telegram.org/bot<TOKEN>/getUpdates
   ```
4. В ответе найдите `"chat": { "id": 123456789 }` — это ваш `TELEGRAM_CHAT_ID`
5. Вставьте токен и id в `.env`

После этого каждый RSVP-ответ будет приходить вам в Telegram.

---

## Структура проекта

```
wedding/
├── main.py              # FastAPI — роуты и логика
├── models.py            # SQLAlchemy модель RSVP
├── database.py          # Подключение к БД
├── config.py            # Настройки из .env (pydantic-settings)
├── telegram_notify.py   # Отправка уведомлений в Telegram
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── nginx.conf
├── .env.example
├── templates/
│   ├── index.html       # Главная страница
│   ├── thank_you.html   # Страница после RSVP
│   └── admin.html       # Панель администратора
└── static/
    ├── css/style.css
    ├── js/main.js       # Карусель, таймер, анимации
    └── images/          # Фото, видео, иконки
```
