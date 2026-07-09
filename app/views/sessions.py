from datetime import datetime, date

from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.crud.session import get_sessions, get_session
from app.crud.seat import get_seats_by_hall
from app.crud.booking import get_bookings_by_session, create_booking
from app.schemas.booking import BookingCreate
from app.exceptions import DatabaseError

router = APIRouter()
templates = Jinja2Templates(directory="templates")


UA_DAYS = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Нд"]


@router.get("/sessions", response_class=HTMLResponse)
async def sessions_list(request: Request, db: AsyncSession = Depends(get_db)):
    today = date.today()
    all_sessions = await get_sessions(db, limit=500)
    sorted_sessions = sorted(
        (s for s in all_sessions if s.start_time.date() >= today),
        key=lambda s: s.start_time,
    )

    grouped: dict = {}
    for s in sorted_sessions:
        d = s.start_time.date()
        if d not in grouped:
            day_name = UA_DAYS[d.weekday()]
            grouped[d] = {"label": f"{day_name}, {d.strftime('%d.%m')}", "sessions": []}
        grouped[d]["sessions"].append(s)

    return templates.TemplateResponse(request=request, name="sessions.html", context={
        "grouped_sessions": grouped,
        "active": "sessions",
    })


@router.get("/booking/{session_id}", response_class=HTMLResponse)
async def booking_page(session_id: int, request: Request, db: AsyncSession = Depends(get_db),
                       message: str = None, success: bool = False):
    session = await get_session(db, session_id)
    if not session:
        return HTMLResponse("<h1>Сеанс не знайдено</h1>", status_code=404)

    seats = await get_seats_by_hall(db, session.hall_id)
    bookings = await get_bookings_by_session(db, session_id)
    taken_seat_ids = {b.seat_id for b in bookings}

    rows: dict[int, list] = {}
    for seat in seats:
        rows.setdefault(seat.row, []).append(seat)
    for row in rows.values():
        row.sort(key=lambda s: s.number)

    return templates.TemplateResponse(request=request, name="booking.html", context={
        "session": session,
        "rows": rows,
        "taken_seat_ids": taken_seat_ids,
        "message": message,
        "success": success,
        "active": "sessions",
    })


@router.post("/booking/{session_id}/confirm")
async def booking_confirm(session_id: int, request: Request,
                          user_id: int = Form(...), seat_id: int = Form(...),
                          db: AsyncSession = Depends(get_db)):
    try:
        await create_booking(db, BookingCreate(
            user_id=user_id, session_id=session_id, seat_id=seat_id,
        ))
        return RedirectResponse(
            url=f"/booking/{session_id}?message=Бронювання+успішне!&success=true",
            status_code=303,
        )
    except DatabaseError:
        return RedirectResponse(
            url=f"/booking/{session_id}?message=Помилка:+місце+вже+зайняте&success=false",
            status_code=303,
        )
