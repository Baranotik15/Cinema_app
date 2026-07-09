from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.crud.movie import get_movie
from app.crud.session import get_sessions_by_movie

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/movies/{movie_id}", response_class=HTMLResponse)
async def movie_detail(movie_id: int, request: Request, db: AsyncSession = Depends(get_db)):
    movie = await get_movie(db, movie_id)
    if not movie:
        return HTMLResponse("<h1>Фільм не знайдено</h1>", status_code=404)
    sessions = await get_sessions_by_movie(db, movie_id)
    return templates.TemplateResponse(request=request, name="movie_detail.html", context={
        "movie": movie,
        "sessions": sessions,
        "active": "movies",
    })
