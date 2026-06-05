import httpx

from config import settings


async def send_rsvp_notification(name: str, attending: str, food_note: str, comment: str) -> None:
    if not settings.TELEGRAM_BOT_TOKEN or not settings.TELEGRAM_CHAT_ID:
        return

    attending_text = "✅ Придёт" if attending == "yes" else "❌ Не придёт"
    food_text = food_note or "не указано"
    comment_text = comment or "нет"

    text = (
        "🎊 *Новый ответ на приглашение!*\n\n"
        f"👤 Имя: {name}\n"
        f"{attending_text}\n"
        f"🍽 Пожелания по еде: {food_text}\n"
        f"💬 Комментарий: {comment_text}\n\n"
        f"📅 Свадьба: 19.09.2026 12:00"
    )

    url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
    async with httpx.AsyncClient() as client:
        await client.post(url, json={
            "chat_id": settings.TELEGRAM_CHAT_ID,
            "text": text,
            "parse_mode": "Markdown",
        })