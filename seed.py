"""
WARNING: seed.py fully resets the database!
All existing data will be deleted. Use in development only.

The server does NOT need to be running — data is inserted directly via SQLAlchemy.

Usage:
    python seed.py
"""
import asyncio
import os
import subprocess
import sys
from datetime import datetime, timedelta

DB_PATH = "sql_app.db"


def day(offset: int, hour: int, minute: int = 0) -> str:
    dt = datetime.today().replace(hour=hour, minute=minute, second=0, microsecond=0)
    dt += timedelta(days=offset)
    return dt.isoformat()


def reset_db():
    print("=" * 50)
    print("! WARNING: full database reset")
    print("=" * 50)
    answer = input("Continue? All data will be deleted [y/N]: ").strip().lower()
    if answer != "y":
        print("Cancelled.")
        sys.exit(0)

    if os.path.exists(DB_PATH):
        try:
            os.remove(DB_PATH)
            print(f"[OK] Deleted {DB_PATH}")
        except PermissionError:
            print(f"[ERR] Cannot delete {DB_PATH} — stop the server and try again.")
            sys.exit(1)

    result = subprocess.run(["alembic", "upgrade", "head"], capture_output=True, text=True)
    if result.returncode != 0:
        print("[ERR] alembic upgrade head failed:")
        print(result.stderr)
        sys.exit(1)
    print("[OK] Migrations applied\n")


async def seed():
    from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
    from app.models.genre import Genre
    from app.models.actor import Actor
    from app.models.movie import Movie
    from app.models.user import User
    from app.models.hall import Hall
    from app.models.session import Session
    from app.models.seat import Seat

    PLACEHOLDER_POSTER = "https://placehold.co/300x450/png"
    PLACEHOLDER_ACTOR  = "https://placehold.co/200x200/png"

    engine = create_async_engine("sqlite+aiosqlite:///./sql_app.db", echo=False)
    mk = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

    async with mk() as db:
        # --- Genres ---
        print("Genres...")
        genre_names = [
            "Action", "Drama", "Comedy", "Thriller", "Sci-Fi",
            "Horror", "Romance", "Animation", "Documentary", "Fantasy",
            "Crime", "Adventure", "Mystery", "Biography", "History",
        ]
        genres = {}
        for name in genre_names:
            g = Genre(name=name)
            db.add(g)
            await db.flush()
            genres[name] = g
            print(f"  [OK] {name} -> id={g.id}")
        await db.commit()

        # --- Actors ---
        print("\nActors...")
        actors_data = [
            ("Tom Hanks",           50, "male"),
            ("Leonardo DiCaprio",   48, "male"),
            ("Scarlett Johansson",  38, "female"),
            ("Brad Pitt",           59, "male"),
            ("Meryl Streep",        73, "female"),
            ("Robert Downey Jr.",   58, "male"),
            ("Cate Blanchett",      54, "female"),
            ("Morgan Freeman",      86, "male"),
            ("Natalie Portman",     42, "female"),
            ("Christian Bale",      49, "male"),
            ("Anne Hathaway",       41, "female"),
            ("Joaquin Phoenix",     49, "male"),
            ("Emma Stone",          35, "female"),
            ("Ryan Gosling",        43, "male"),
            ("Viola Davis",         58, "female"),
            ("Denzel Washington",   69, "male"),
            ("Jennifer Lawrence",   33, "female"),
            ("Matt Damon",          53, "male"),
            ("Charlize Theron",     48, "female"),
            ("Tom Hardy",           46, "male"),
        ]
        actors = {}
        for name, age, gender in actors_data:
            a = Actor(name=name, age=age, gender=gender,
                      bio="Award-winning actor/actress known for numerous blockbuster films.",
                      image_url=PLACEHOLDER_ACTOR)
            db.add(a)
            await db.flush()
            actors[name] = a
            print(f"  [OK] {name} -> id={a.id}")
        await db.commit()

        # --- Movies ---
        print("\nMovies...")
        movies_data = [
            {
                "title": "Inception",
                "description": "A thief who steals corporate secrets through dream-sharing technology is given the inverse task of planting an idea.",
                "duration": 148, "year": 2010, "rating": 8.8,
                "actors": ["Leonardo DiCaprio", "Tom Hardy", "Anne Hathaway"],
                "genres": ["Action", "Sci-Fi", "Thriller"],
            },
            {
                "title": "Forrest Gump",
                "description": "The presidencies of Kennedy and Johnson, the Vietnam War, and other historical events unfold through the eyes of an Alabama man.",
                "duration": 142, "year": 1994, "rating": 8.8,
                "actors": ["Tom Hanks"],
                "genres": ["Drama", "Comedy", "Romance"],
            },
            {
                "title": "Fight Club",
                "description": "An insomniac office worker and a devil-may-care soap maker form an underground fight club.",
                "duration": 139, "year": 1999, "rating": 8.8,
                "actors": ["Brad Pitt"],
                "genres": ["Drama", "Thriller", "Mystery"],
            },
            {
                "title": "The Dark Knight",
                "description": "Batman raises the stakes in his war on crime with the help of Lt. Jim Gordon and DA Harvey Dent.",
                "duration": 152, "year": 2008, "rating": 9.0,
                "actors": ["Christian Bale", "Morgan Freeman"],
                "genres": ["Action", "Crime", "Drama"],
            },
            {
                "title": "Interstellar",
                "description": "A team of explorers travel through a wormhole in space in an attempt to ensure humanity's survival.",
                "duration": 169, "year": 2014, "rating": 8.7,
                "actors": ["Matt Damon", "Anne Hathaway"],
                "genres": ["Sci-Fi", "Adventure", "Drama"],
            },
            {
                "title": "The Matrix",
                "description": "A computer hacker learns from mysterious rebels about the true nature of his reality.",
                "duration": 136, "year": 1999, "rating": 8.7,
                "actors": ["Charlize Theron"],
                "genres": ["Action", "Sci-Fi"],
            },
            {
                "title": "Avengers: Endgame",
                "description": "After the devastating events of Infinity War, the Avengers assemble once more.",
                "duration": 181, "year": 2019, "rating": 8.4,
                "actors": ["Robert Downey Jr.", "Scarlett Johansson"],
                "genres": ["Action", "Adventure", "Fantasy"],
            },
            {
                "title": "Joker",
                "description": "A mentally troubled comedian embarks on a downward spiral of revolution and bloody crime.",
                "duration": 122, "year": 2019, "rating": 8.4,
                "actors": ["Joaquin Phoenix"],
                "genres": ["Crime", "Drama", "Thriller"],
            },
            {
                "title": "La La Land",
                "description": "A jazz musician and an aspiring actress fall in love while each pursuing their dreams in Los Angeles.",
                "duration": 128, "year": 2016, "rating": 8.0,
                "actors": ["Ryan Gosling", "Emma Stone"],
                "genres": ["Romance", "Drama", "Comedy"],
            },
            {
                "title": "Black Swan",
                "description": "A committed dancer wins the lead role in a production of Tchaikovsky's Swan Lake.",
                "duration": 108, "year": 2010, "rating": 8.0,
                "actors": ["Natalie Portman"],
                "genres": ["Drama", "Horror", "Mystery"],
            },
            {
                "title": "Mad Max: Fury Road",
                "description": "In a post-apocalyptic wasteland, a woman rebels against a tyrannical ruler.",
                "duration": 120, "year": 2015, "rating": 8.1,
                "actors": ["Tom Hardy", "Charlize Theron"],
                "genres": ["Action", "Adventure", "Sci-Fi"],
            },
            {
                "title": "The Devil Wears Prada",
                "description": "A smart but sensible new graduate lands a job as an assistant to Miranda Priestly.",
                "duration": 109, "year": 2006, "rating": 6.9,
                "actors": ["Meryl Streep", "Anne Hathaway"],
                "genres": ["Comedy", "Drama"],
            },
            {
                "title": "Shutter Island",
                "description": "A U.S. Marshal investigates the disappearance of a murderer who escaped from a hospital for the criminally insane.",
                "duration": 138, "year": 2010, "rating": 8.1,
                "actors": ["Leonardo DiCaprio"],
                "genres": ["Mystery", "Thriller", "Drama"],
            },
            {
                "title": "The Revenant",
                "description": "A frontiersman on a fur trading expedition fights for survival after being mauled by a bear.",
                "duration": 156, "year": 2015, "rating": 8.0,
                "actors": ["Leonardo DiCaprio", "Tom Hardy"],
                "genres": ["Adventure", "Drama", "History"],
            },
            {
                "title": "Her",
                "description": "A lonely writer develops an unlikely relationship with an operating system.",
                "duration": 126, "year": 2013, "rating": 8.0,
                "actors": ["Scarlett Johansson"],
                "genres": ["Drama", "Romance", "Sci-Fi"],
            },
        ]
        movies = {}
        for md in movies_data:
            m = Movie(
                title=md["title"], description=md["description"],
                duration=md["duration"], year=md["year"], rating=md["rating"],
                poster_url=PLACEHOLDER_POSTER,
                actors=[actors[n] for n in md["actors"] if n in actors],
                genres=[genres[n] for n in md["genres"] if n in genres],
            )
            db.add(m)
            await db.flush()
            movies[m.title] = m
            print(f"  [OK] {m.title} -> id={m.id}")
        await db.commit()

        # --- Users ---
        print("\nUsers...")
        users_data = [
            ("john_doe",    "john@example.com",    "password123"),
            ("jane_doe",    "jane@example.com",    "password123"),
            ("alice_smith", "alice@example.com",   "password123"),
            ("bob_jones",   "bob@example.com",     "password123"),
            ("carol_white", "carol@example.com",   "password123"),
            ("david_black", "david@example.com",   "password123"),
            ("eva_green",   "eva@example.com",     "password123"),
            ("frank_hill",  "frank@example.com",   "password123"),
            ("grace_lee",   "grace@example.com",   "password123"),
            ("henry_king",  "henry@example.com",   "password123"),
        ]
        users = []
        for username, email, password in users_data:
            u = User(username=username, email=email, hashed_password=password)
            db.add(u)
            await db.flush()
            users.append(u)
            print(f"  [OK] {username} -> id={u.id}")
        await db.commit()

        # --- Halls + Seats ---
        print("\nHalls...")
        halls_data = [
            ("Hall 1",    120, "2D",   10, 12),
            ("Hall 2",     80, "3D",    8, 10),
            ("Hall IMAX", 200, "IMAX", 10, 20),
            ("Hall 3",    100, "2D",   10, 10),
            ("Hall 4",     60, "3D",    6, 10),
            ("Hall VIP",   40, "IMAX",  4, 10),
        ]
        halls = {}
        for name, capacity, hall_type, rows, cols in halls_data:
            h = Hall(name=name, capacity=capacity, hall_type=hall_type)
            db.add(h)
            await db.flush()
            halls[name] = h
            print(f"  [OK] {name} -> id={h.id}")
            for row in range(1, rows + 1):
                for col in range(1, cols + 1):
                    db.add(Seat(hall_id=h.id, row=row, number=col))
            await db.flush()
        await db.commit()

        # --- Sessions ---
        print("\nSessions...")
        sessions_data = [
            ("Inception",            "Hall 1",    day(0,  10), 12.5),
            ("Forrest Gump",         "Hall 2",    day(0,  13), 14.0),
            ("Inception",            "Hall IMAX", day(0,  20), 22.0),
            ("Fight Club",           "Hall IMAX", day(0,  22), 20.0),
            ("The Dark Knight",      "Hall 1",    day(1,  11), 15.0),
            ("Forrest Gump",         "Hall 3",    day(1,  18), 13.0),
            ("The Dark Knight",      "Hall IMAX", day(1,  21), 25.0),
            ("The Matrix",           "Hall 3",    day(2,  12), 12.0),
            ("Interstellar",         "Hall 2",    day(2,  15), 16.0),
            ("Interstellar",         "Hall VIP",  day(2,  19), 35.0),
            ("Avengers: Endgame",    "Hall IMAX", day(3,  14), 24.0),
            ("Joker",                "Hall 4",    day(3,  17), 13.5),
            ("Avengers: Endgame",    "Hall 1",    day(3,  20), 18.0),
            ("La La Land",           "Hall 2",    day(4,  16), 11.0),
            ("Black Swan",           "Hall 4",    day(4,  20), 12.0),
            ("The Devil Wears Prada","Hall 3",    day(5,  11), 10.0),
            ("Mad Max: Fury Road",   "Hall IMAX", day(5,  15), 22.0),
            ("Shutter Island",       "Hall 1",    day(5,  19), 13.0),
            ("The Revenant",         "Hall IMAX", day(6,  17), 23.0),
            ("Her",                  "Hall VIP",  day(6,  20), 30.0),
            ("Black Swan",           "Hall 1",    day(7,  10), 12.0),
            ("Shutter Island",       "Hall 2",    day(7,  14), 13.0),
            ("La La Land",           "Hall IMAX", day(7,  19), 21.0),
            ("Mad Max: Fury Road",   "Hall 3",    day(8,  12), 15.0),
            ("Her",                  "Hall 4",    day(8,  18), 14.0),
            ("Joker",                "Hall IMAX", day(9,  20), 22.0),
        ]
        session_count = 0
        for title, hall_name, start_time, price in sessions_data:
            m = movies.get(title)
            h = halls.get(hall_name)
            if m and h:
                s = Session(
                    movie_id=m.id, hall_id=h.id,
                    start_time=datetime.fromisoformat(start_time),
                    price=price, status="scheduled",
                )
                db.add(s)
                session_count += 1
        await db.commit()
        print(f"  [OK] {session_count} sessions created")

    await engine.dispose()

    print("\n" + "=" * 50)
    print("Seed completed!")
    print(f"  Genres:   {len(genre_names)}")
    print(f"  Actors:   {len(actors_data)}")
    print(f"  Movies:   {len(movies_data)}")
    print(f"  Users:    {len(users_data)}")
    print(f"  Halls:    {len(halls_data)}")
    print(f"  Sessions: {session_count}")
    print("=" * 50)


if __name__ == "__main__":
    reset_db()
    asyncio.run(seed())
