from fastapi import FastAPI
from app.api import movies, actors, genres, users, halls, sessions, bookings
from app.views import home, movies as movie_views, sessions as session_views

app = FastAPI(title="Cinema App", version="1.0.0")

app.include_router(home.router)
app.include_router(movie_views.router)
app.include_router(session_views.router)
app.include_router(genres.router,   prefix="/api/v1/genres",   tags=["Genres"])
app.include_router(actors.router,   prefix="/api/v1/actors",   tags=["Actors"])
app.include_router(movies.router,   prefix="/api/v1/movies",   tags=["Movies"])
app.include_router(users.router,    prefix="/api/v1/users",    tags=["Users"])
app.include_router(halls.router,    prefix="/api/v1/halls",    tags=["Halls"])
app.include_router(sessions.router, prefix="/api/v1/sessions", tags=["Sessions"])
app.include_router(bookings.router, prefix="/api/v1/bookings", tags=["Bookings"])
