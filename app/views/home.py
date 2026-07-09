from datetime import date

from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.crud.movie import get_movies
from app.crud.session import get_sessions

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/", response_class=HTMLResponse)
async def home(request: Request, db: AsyncSession = Depends(get_db)):
    today = date.today()
    all_sessions = await get_sessions(db, limit=500)
    future_sessions = [s for s in all_sessions if s.start_time.date() >= today]

    movie_ids_with_future = {s.movie_id for s in future_sessions}
    all_movies = await get_movies(db, limit=100)
    movies = [m for m in all_movies if m.id in movie_ids_with_future][:8]

    sessions = sorted(future_sessions, key=lambda s: s.start_time)[:10]

    return templates.TemplateResponse(request=request, name="index.html", context={
        "movies": movies,
        "sessions": sessions,
        "active": "home",
    })
