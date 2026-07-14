"""
Тесты для свадебного сайта.
Используется TestClient из FastAPI — реальные HTTP-запросы без запуска сервера.
БД в памяти (SQLite :memory:) — тесты не трогают боевые данные.
"""
from unittest.mock import AsyncMock, patch


# ── Главная страница ───────────────────────────────────────────────────────────

class TestIndex:
    def test_returns_200(self, client):
        r = client.get("/")
        assert r.status_code == 200

    def test_contains_names(self, client):
        r = client.get("/")
        assert "Артём" in r.text
        assert "Яна" in r.text

    def test_contains_wedding_date(self, client):
        r = client.get("/")
        assert "2026" in r.text

    def test_contains_rsvp_form(self, client):
        r = client.get("/")
        assert 'action="/rsvp"' in r.text

    def test_contains_zagс_address(self, client):
        r = client.get("/")
        assert "Монетная" in r.text


# ── RSVP форма ────────────────────────────────────────────────────────────────

class TestRSVP:
    def test_attending_yes_redirects_to_thank_you(self, client):
        with patch("main.send_rsvp_notification", new_callable=AsyncMock):
            r = client.post(
                "/rsvp",
                data={"name": "Иван Иванов", "attending": "yes"},
                follow_redirects=False,
            )
        assert r.status_code == 303
        assert "/thank-you?attending=yes" in r.headers["location"]

    def test_attending_no_redirects_to_thank_you(self, client):
        with patch("main.send_rsvp_notification", new_callable=AsyncMock):
            r = client.post(
                "/rsvp",
                data={"name": "Мария Петрова", "attending": "no"},
                follow_redirects=False,
            )
        assert r.status_code == 303
        assert "/thank-you?attending=no" in r.headers["location"]

    def test_empty_name_returns_422(self, client):
        r = client.post("/rsvp", data={"name": "", "attending": "yes"})
        assert r.status_code == 422

    def test_invalid_attending_value_returns_422(self, client):
        r = client.post("/rsvp", data={"name": "Тест", "attending": "maybe"})
        assert r.status_code == 422

    def test_duplicate_name_updates_existing(self, client):
        with patch("main.send_rsvp_notification", new_callable=AsyncMock):
            client.post("/rsvp", data={"name": "Алексей", "attending": "yes"})
            client.post("/rsvp", data={"name": "Алексей", "attending": "no"})

        r = client.get("/admin", auth=("admin", "changeme"))
        assert r.status_code == 200
        # Должна быть только одна запись
        assert r.text.count("Алексей") == 1

    def test_comment_is_saved(self, client):
        with patch("main.send_rsvp_notification", new_callable=AsyncMock):
            client.post(
                "/rsvp",
                data={"name": "Ольга", "attending": "yes", "comment": "Поздравляю!"},
            )
        r = client.get("/admin", auth=("admin", "changeme"))
        assert "Поздравляю!" in r.text

    def test_telegram_notification_is_called(self, client):
        with patch("main.send_rsvp_notification", new_callable=AsyncMock) as mock_tg:
            client.post("/rsvp", data={"name": "Сергей", "attending": "yes"})
        mock_tg.assert_called_once_with("Сергей", "yes", "", "")


# ── Страница благодарности ────────────────────────────────────────────────────

class TestThankYou:
    def test_attending_yes_returns_200(self, client):
        r = client.get("/thank-you?attending=yes")
        assert r.status_code == 200

    def test_attending_no_returns_200(self, client):
        r = client.get("/thank-you?attending=no")
        assert r.status_code == 200


# ── Календарь ─────────────────────────────────────────────────────────────────

class TestCalendar:
    def test_returns_ics_file(self, client):
        r = client.get("/calendar.ics")
        assert r.status_code == 200
        assert "text/calendar" in r.headers["content-type"]

    def test_ics_contains_event(self, client):
        r = client.get("/calendar.ics")
        assert "BEGIN:VCALENDAR" in r.text
        assert "BEGIN:VEVENT" in r.text
        assert "20260919" in r.text

    def test_ics_has_correct_location(self, client):
        r = client.get("/calendar.ics")
        assert "Монетная" in r.text


# ── Админ панель ──────────────────────────────────────────────────────────────

class TestAdmin:
    def test_requires_auth(self, client):
        r = client.get("/admin")
        assert r.status_code == 401

    def test_wrong_password_returns_401(self, client):
        r = client.get("/admin", auth=("admin", "wrongpassword"))
        assert r.status_code == 401

    def test_correct_password_returns_200(self, client):
        r = client.get("/admin", auth=("admin", "changeme"))
        assert r.status_code == 200

    def test_shows_guest_list(self, client):
        with patch("main.send_rsvp_notification", new_callable=AsyncMock):
            client.post("/rsvp", data={"name": "Дмитрий", "attending": "yes"})

        r = client.get("/admin", auth=("admin", "changeme"))
        assert "Дмитрий" in r.text

    def test_shows_correct_stats(self, client):
        with patch("main.send_rsvp_notification", new_callable=AsyncMock):
            client.post("/rsvp", data={"name": "Гость1", "attending": "yes"})
            client.post("/rsvp", data={"name": "Гость2", "attending": "yes"})
            client.post("/rsvp", data={"name": "Гость3", "attending": "no"})

        r = client.get("/admin", auth=("admin", "changeme"))
        assert r.status_code == 200


# ── Статика ───────────────────────────────────────────────────────────────────

class TestStatic:
    def test_css_is_accessible(self, client):
        r = client.get("/static/css/style.css")
        assert r.status_code == 200

    def test_js_is_accessible(self, client):
        r = client.get("/static/js/main.js")
        assert r.status_code == 200

    def test_zags_photo_is_accessible(self, client):
        r = client.get("/static/images/zags.jpg")
        assert r.status_code == 200
