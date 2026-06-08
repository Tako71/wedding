# Мониторинг

Стек: **Netdata** (системные метрики) + **Uptime Kuma** (доступность) + **Grafana Cloud** (исторические графики и логи).

```
Netdata ──────────────────────────────► Grafana Cloud
  (CPU, RAM, диск, сеть, Docker)          (исторические дашборды)
                │
                ▼
           Grafana Alloy
           (push каждые 15s)

Uptime Kuma ──────────────────────────► Telegram
  (пинг сайта каждую минуту)              (алерт если упал)

Nginx access.log ─────────────────────► Grafana Cloud Loki
  (трафик в реальном времени)             (поиск по логам)
```

---

## Шаг 1 — Создать htpasswd для защиты панелей

Выполнить на сервере (один раз):

```bash
apt-get install -y apache2-utils
cd /opt/wedding
htpasswd -c monitoring/htpasswd admin
# Введите пароль — он будет защищать /uptime/ и /netdata/
```

---

## Шаг 2 — Запустить мониторинг

```bash
cd /opt/wedding
git pull origin main
sed -i 's/YOUR_DOMAIN/piletskigroup.ru/g' nginx.conf
docker compose up -d --build
```

Панели будут доступны:
- **https://piletskigroup.ru/uptime/** — Uptime Kuma
- **https://piletskigroup.ru/netdata/** — Netdata

---

## Шаг 3 — Настроить Uptime Kuma

1. Откройте **https://piletskigroup.ru/uptime/**
2. Создайте аккаунт (первый вход)
3. Нажмите **Add New Monitor**:
   - Monitor Type: `HTTP(s)`
   - URL: `https://piletskigroup.ru`
   - Heartbeat Interval: `60` секунд
4. Настройте Telegram-уведомления:
   - Settings → Notifications → Add → **Telegram**
   - Bot Token: `8625521328:AAF0FNBFLjx83gSbI9mq1TgLqzm32q3eB_Q`
   - Chat ID: `571682214`
5. Нажмите **Test** — должно прийти сообщение в Telegram

---

## Шаг 4 — Подключить Grafana Cloud

### 4.1 Создать аккаунт

Зарегистрируйтесь на [grafana.com](https://grafana.com) → выберите **Free** план.  
Получите доступ к своему Grafana Cloud Stack.

### 4.2 Получить credentials для Prometheus

1. В Grafana Cloud откройте **Connections → Add new connection → Prometheus**
2. Скопируйте:
   - **Remote Write URL** (вида `https://prometheus-prod-xx.grafana.net/api/prom/push`)
   - **Username / Instance ID**
   - Создайте **API Key** с ролью `MetricsPublisher`

### 4.3 Получить credentials для Loki (логи)

1. **Connections → Add new connection → Loki**
2. Скопируйте:
   - **Loki URL** (вида `https://logs-prod-xx.grafana.net/loki/api/v1/push`)
   - **User ID**
   - Используйте тот же **API Key**

### 4.4 Установить Grafana Alloy на сервере

```bash
# Установка
wget -q -O - https://apt.grafana.com/gpg.key | gpg --dearmor > /etc/apt/keyrings/grafana.gpg
echo "deb [signed-by=/etc/apt/keyrings/grafana.gpg] https://apt.grafana.com stable main" \
  > /etc/apt/sources.list.d/grafana.list
apt-get update && apt-get install -y alloy
```

### 4.5 Заполнить конфиг Alloy

```bash
cd /opt/wedding
nano monitoring/alloy.config
# Замените YOUR_GRAFANA_CLOUD_* на реальные значения из шага 4.2 и 4.3
```

```bash
# Скопировать конфиг и запустить
cp monitoring/alloy.config /etc/alloy/config.alloy
systemctl enable alloy
systemctl start alloy
systemctl status alloy
```

### 4.6 Проверить что метрики поступают

В Grafana Cloud → **Explore** → выберите datasource **Prometheus** → введите:
```
netdata_system_cpu_percentage
```
Должны появиться данные.

### 4.7 Импортировать готовый дашборд

1. В Grafana: **Dashboards → Import**
2. Введите ID: **7107** (официальный Netdata dashboard)
3. Выберите свой Prometheus datasource
4. Готово — видны CPU, RAM, диск, сеть

---

## Что смотреть в Grafana

| Метрика | Что означает |
|---------|-------------|
| `netdata_system_cpu_percentage` | Загрузка CPU сервера |
| `netdata_system_ram_MiB` | Использование RAM |
| `netdata_disk_io_KiB` | Нагрузка на диск |
| `netdata_net_net_kilobits` | Входящий/исходящий трафик |
| `netdata_nginx_connections` | Активные подключения к Nginx |
| Логи в Loki | Все запросы к сайту в реальном времени |

---

## Быстрые команды для отладки

```bash
# Статус всех контейнеров мониторинга
docker compose ps uptime-kuma netdata

# Логи Netdata
docker compose logs -f netdata

# Логи Uptime Kuma
docker compose logs -f uptime-kuma

# Статус Grafana Alloy
systemctl status alloy
journalctl -u alloy -f
```
