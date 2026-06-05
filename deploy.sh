#!/bin/bash
# =============================================================================
# Скрипт деплоя свадебного сайта на VPS (Ubuntu 22.04+)
# Запускать от root или через sudo
# =============================================================================

set -e  # Остановить выполнение при любой ошибке

DOMAIN="YOUR_DOMAIN"          # ← Замените на ваш домен
EMAIL="YOUR_EMAIL"            # ← Замените на ваш email (для SSL)
REPO="YOUR_GITHUB_REPO_URL"   # ← Замените на URL вашего GitHub репозитория

# ── 1. Установка Docker ───────────────────────────────────────────────────────
echo ">>> Устанавливаем Docker..."
apt-get update -y
apt-get install -y ca-certificates curl gnupg
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
chmod a+r /etc/apt/keyrings/docker.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
  https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" \
  > /etc/apt/sources.list.d/docker.list
apt-get update -y
apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
echo "Docker установлен: $(docker --version)"

# ── 2. Клонирование репозитория ───────────────────────────────────────────────
echo ">>> Клонируем репозиторий..."
git clone "$REPO" /opt/wedding
cd /opt/wedding

# ── 3. Настройка .env ─────────────────────────────────────────────────────────
echo ">>> Создаём .env..."
cp .env.example .env
echo ""
echo "⚠️  Заполните /opt/wedding/.env своими данными:"
echo "    nano /opt/wedding/.env"
echo ""
read -p "Нажмите Enter после заполнения .env..." _

# ── 4. Замена домена в nginx.conf ─────────────────────────────────────────────
echo ">>> Прописываем домен $DOMAIN в nginx.conf..."
sed -i "s/YOUR_DOMAIN/$DOMAIN/g" nginx.conf

# ── 5. Первый запуск — только HTTP (нужен для получения SSL) ──────────────────
echo ">>> Запускаем Nginx на HTTP для верификации домена..."
docker compose up -d nginx

# ── 6. Получение SSL сертификата ──────────────────────────────────────────────
echo ">>> Получаем SSL сертификат Let's Encrypt..."
docker compose run --rm certbot certonly \
  --webroot -w /var/www/certbot \
  --email "$EMAIL" \
  --agree-tos \
  --no-eff-email \
  -d "$DOMAIN" -d "www.$DOMAIN"

# ── 7. Полный запуск всех сервисов ────────────────────────────────────────────
echo ">>> Запускаем все сервисы..."
docker compose up -d --build

echo ""
echo "✅ Готово! Сайт доступен по адресу: https://$DOMAIN"
echo ""
echo "Полезные команды:"
echo "  docker compose logs -f app     # логи FastAPI"
echo "  docker compose logs -f nginx   # логи Nginx"
echo "  docker compose restart app     # перезапустить приложение"
echo "  docker compose down            # остановить всё"
