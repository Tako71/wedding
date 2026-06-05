import secrets
from typing import Annotated

from fastapi import FastAPI, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy.orm import Session

from config import settings
from database import get_db, init_db
from models import RSVP
from telegram_notify import send_rsvp_notification

app = FastAPI(docs_url=None, redoc_url=None)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")
security = HTTPBasic()


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {
        "request": request,
        "wedding_date": settings.WEDDING_DATE,
    })


@app.post("/rsvp")
async def rsvp(
    request: Request,
    name: Annotated[str, Form()],
    attending: Annotated[str, Form()],
    food_note: Annotated[str, Form()] = "",
    comment: Annotated[str, Form()] = "",
    db: Session = Depends(get_db),
):
    name = name.strip()
    if not name or attending not in ("yes", "no"):
        raise HTTPException(status_code=422, detail="Некорректные данные")

    existing = db.query(RSVP).filter(RSVP.name == name).first()
    if existing:
        existing.attending = attending
        existing.food_note = food_note.strip() or None
        existing.comment = comment.strip() or None
    else:
        record = RSVP(
            name=name,
            attending=attending,
            food_note=food_note.strip() or None,
            comment=comment.strip() or None,
        )
        db.add(record)

    db.commit()

    await send_rsvp_notification(name, attending, food_note, comment)

    return RedirectResponse(url=f"/thank-you?attending={attending}", status_code=303)


@app.get("/calendar.ics")
async def calendar_ics():
    ics = (
        "BEGIN:VCALENDAR\r\n"
        "VERSION:2.0\r\n"
        "PRODID:-//Wedding//RU\r\n"
        "BEGIN:VEVENT\r\n"
        "UID:wedding-artem-yana-2026@wedding\r\n"
        "DTSTAMP:20260606T000000Z\r\n"
        "DTSTART:20260919T113000\r\n"
        "DTEND:20260919T150000\r\n"
        "SUMMARY:Свадьба Артёма & Яны 💍\r\n"
        "DESCRIPTION:Сбор гостей в 11:30\\nЦеремония в 12:00\\nФотосессия в 12:30\r\n"
        "LOCATION:Большая Монетная ул.\\, 17-19\\, Санкт-Петербург\r\n"
        "END:VEVENT\r\n"
        "END:VCALENDAR\r\n"
    )
    return Response(
        content=ics,
        media_type="text/calendar",
        headers={"Content-Disposition": "attachment; filename=wedding.ics"},
    )


@app.get("/thank-you", response_class=HTMLResponse)
async def thank_you(request: Request, attending: str = "yes"):
    return templates.TemplateResponse("thank_you.html", {
        "request": request,
        "attending": attending,
    })


def _check_admin(credentials: HTTPBasicCredentials = Depends(security)):
    correct = secrets.compare_digest(
        credentials.password.encode(), settings.SECRET_ADMIN_PASSWORD.encode()
    )
    if not correct:
        raise HTTPException(
            status_code=401,
            detail="Неверный пароль",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


@app.get("/admin", response_class=HTMLResponse)
async def admin(
    request: Request,
    _: str = Depends(_check_admin),
    db: Session = Depends(get_db),
):
    guests = db.query(RSVP).order_by(RSVP.created_at.desc()).all()
    yes_count = sum(1 for g in guests if g.attending == "yes")
    no_count = len(guests) - yes_count
    return templates.TemplateResponse("admin.html", {
        "request": request,
        "guests": guests,
        "yes_count": yes_count,
        "no_count": no_count,
    })