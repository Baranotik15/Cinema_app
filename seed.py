import json
import urllib.request
import urllib.error

BASE_URL = "http://127.0.0.1:8000/api/v1"

PLACEHOLDER_POSTER = "https://placehold.co/300x450/png"
PLACEHOLDER_ACTOR  = "https://placehold.co/200x200/png"


def post(path: str, data: dict) -> dict | None:
    url = f"{BASE_URL}{path}"
    body = json.dumps(data).encode("utf-8")
    req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req) as resp:
            result = json.loads(resp.read())
            print(f"[OK] POST {path} -> id={result.get('id')}")
            return result
    except urllib.error.HTTPError as e:
        print(f"[ERR] POST {path} -> {e.code}: {e.read().decode()}")
        return None


def main():
    # --- Genres ---
    genre_names = [
        "Action", "Drama", "Comedy", "Thriller", "Sci-Fi",
        "Horror", "Romance", "Animation", "Documentary", "Fantasy",
        "Crime", "Adventure", "Mystery", "Biography", "History",
    ]
    genres = {}
    for name in genre_names:
        g = post("/genres/", {"name": name})
        if g:
            genres[name] = g["id"]

    # --- Actors ---
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
        a = post("/actors/", {
            "name": name,
            "bio": f"Award-winning actor/actress known for numerous blockbuster films.",
            "age": age,
            "gender": gender,
            "image_url": PLACEHOLDER_ACTOR,
        })
        if a:
            actors[name] = a["id"]

    # --- Movies ---
    movies_data = [
        {
            "title": "Inception",
            "description": "A thief who steals corporate secrets through dream-sharing technology is given the inverse task of planting an idea.",
            "duration": 148, "year": 2010, "rating": 8.8,
            "poster_url": PLACEHOLDER_POSTER,
            "actor_ids": ["Leonardo DiCaprio", "Tom Hardy", "Anne Hathaway"],
            "genre_ids": ["Action", "Sci-Fi", "Thriller"],
        },
        {
            "title": "Forrest Gump",
            "description": "The presidencies of Kennedy and Johnson, the Vietnam War, and other historical events unfold through the eyes of an Alabama man.",
            "duration": 142, "year": 1994, "rating": 8.8,
            "poster_url": PLACEHOLDER_POSTER,
            "actor_ids": ["Tom Hanks"],
            "genre_ids": ["Drama", "Comedy", "Romance"],
        },
        {
            "title": "Fight Club",
            "description": "An insomniac office worker and a devil-may-care soap maker form an underground fight club.",
            "duration": 139, "year": 1999, "rating": 8.8,
            "poster_url": PLACEHOLDER_POSTER,
            "actor_ids": ["Brad Pitt"],
            "genre_ids": ["Drama", "Thriller", "Mystery"],
        },
        {
            "title": "The Dark Knight",
            "description": "Batman raises the stakes in his war on crime with the help of Lt. Jim Gordon and DA Harvey Dent.",
            "duration": 152, "year": 2008, "rating": 9.0,
            "poster_url": PLACEHOLDER_POSTER,
            "actor_ids": ["Christian Bale", "Morgan Freeman"],
            "genre_ids": ["Action", "Crime", "Drama"],
        },
        {
            "title": "Interstellar",
            "description": "A team of explorers travel through a wormhole in space in an attempt to ensure humanity's survival.",
            "duration": 169, "year": 2014, "rating": 8.7,
            "poster_url": PLACEHOLDER_POSTER,
            "actor_ids": ["Matt Damon", "Anne Hathaway"],
            "genre_ids": ["Sci-Fi", "Adventure", "Drama"],
        },
        {
            "title": "The Matrix",
            "description": "A computer hacker learns from mysterious rebels about the true nature of his reality.",
            "duration": 136, "year": 1999, "rating": 8.7,
            "poster_url": PLACEHOLDER_POSTER,
            "actor_ids": ["Charlize Theron"],
            "genre_ids": ["Action", "Sci-Fi"],
        },
        {
            "title": "Avengers: Endgame",
            "description": "After the devastating events of Infinity War, the Avengers assemble once more.",
            "duration": 181, "year": 2019, "rating": 8.4,
            "poster_url": PLACEHOLDER_POSTER,
            "actor_ids": ["Robert Downey Jr.", "Scarlett Johansson"],
            "genre_ids": ["Action", "Adventure", "Fantasy"],
        },
        {
            "title": "Joker",
            "description": "A mentally troubled comedian embarks on a downward spiral of revolution and bloody crime.",
            "duration": 122, "year": 2019, "rating": 8.4,
            "poster_url": PLACEHOLDER_POSTER,
            "actor_ids": ["Joaquin Phoenix"],
            "genre_ids": ["Crime", "Drama", "Thriller"],
        },
        {
            "title": "La La Land",
            "description": "A jazz musician and an aspiring actress fall in love while each pursuing their dreams in Los Angeles.",
            "duration": 128, "year": 2016, "rating": 8.0,
            "poster_url": PLACEHOLDER_POSTER,
            "actor_ids": ["Ryan Gosling", "Emma Stone"],
            "genre_ids": ["Romance", "Drama", "Comedy"],
        },
        {
            "title": "Black Swan",
            "description": "A committed dancer wins the lead role in a production of Tchaikovsky's Swan Lake.",
            "duration": 108, "year": 2010, "rating": 8.0,
            "poster_url": PLACEHOLDER_POSTER,
            "actor_ids": ["Natalie Portman"],
            "genre_ids": ["Drama", "Horror", "Mystery"],
        },
        {
            "title": "Mad Max: Fury Road",
            "description": "In a post-apocalyptic wasteland, a woman rebels against a tyrannical ruler.",
            "duration": 120, "year": 2015, "rating": 8.1,
            "poster_url": PLACEHOLDER_POSTER,
            "actor_ids": ["Tom Hardy", "Charlize Theron"],
            "genre_ids": ["Action", "Adventure", "Sci-Fi"],
        },
        {
            "title": "The Devil Wears Prada",
            "description": "A smart but sensible new graduate lands a job as an assistant to Miranda Priestly.",
            "duration": 109, "year": 2006, "rating": 6.9,
            "poster_url": PLACEHOLDER_POSTER,
            "actor_ids": ["Meryl Streep", "Anne Hathaway"],
            "genre_ids": ["Comedy", "Drama"],
        },
        {
            "title": "Shutter Island",
            "description": "A U.S. Marshal investigates the disappearance of a murderer who escaped from a hospital for the criminally insane.",
            "duration": 138, "year": 2010, "rating": 8.1,
            "poster_url": PLACEHOLDER_POSTER,
            "actor_ids": ["Leonardo DiCaprio"],
            "genre_ids": ["Mystery", "Thriller", "Drama"],
        },
        {
            "title": "The Revenant",
            "description": "A frontiersman on a fur trading expedition fights for survival after being mauled by a bear.",
            "duration": 156, "year": 2015, "rating": 8.0,
            "poster_url": PLACEHOLDER_POSTER,
            "actor_ids": ["Leonardo DiCaprio", "Tom Hardy"],
            "genre_ids": ["Adventure", "Drama", "History"],
        },
        {
            "title": "Her",
            "description": "A lonely writer develops an unlikely relationship with an operating system.",
            "duration": 126, "year": 2013, "rating": 8.0,
            "poster_url": PLACEHOLDER_POSTER,
            "actor_ids": ["Scarlett Johansson"],
            "genre_ids": ["Drama", "Romance", "Sci-Fi"],
        },
    ]
    movies = {}
    for movie in movies_data:
        movie["actor_ids"] = [actors[n] for n in movie["actor_ids"] if n in actors]
        movie["genre_ids"] = [genres[n] for n in movie["genre_ids"] if n in genres]
        m = post("/movies/", movie)
        if m:
            movies[m["title"]] = m["id"]

    # --- Users ---
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
    users = {}
    for username, email, password in users_data:
        u = post("/users/", {"username": username, "email": email, "password": password})
        if u:
            users[username] = u["id"]

    # --- Halls ---
    halls_data = [
        ("Hall 1",      120, "2D"),
        ("Hall 2",       80, "3D"),
        ("Hall IMAX",   200, "IMAX"),
        ("Hall 3",      100, "2D"),
        ("Hall 4",       60, "3D"),
        ("Hall VIP",     40, "IMAX"),
    ]
    halls = {}
    for name, capacity, hall_type in halls_data:
        h = post("/halls/", {"name": name, "capacity": capacity, "hall_type": hall_type})
        if h:
            halls[name] = h["id"]

    # --- Sessions ---
    sessions_data = [
        ("Inception",           "Hall 1",    "2026-06-15T10:00:00", 12.5,  "scheduled"),
        ("Inception",           "Hall IMAX", "2026-06-15T20:00:00", 22.0,  "scheduled"),
        ("Forrest Gump",        "Hall 2",    "2026-06-15T13:00:00", 14.0,  "scheduled"),
        ("Forrest Gump",        "Hall 3",    "2026-06-16T18:00:00", 13.0,  "scheduled"),
        ("Fight Club",          "Hall IMAX", "2026-06-15T22:00:00", 20.0,  "scheduled"),
        ("The Dark Knight",     "Hall 1",    "2026-06-16T11:00:00", 15.0,  "scheduled"),
        ("The Dark Knight",     "Hall IMAX", "2026-06-16T21:00:00", 25.0,  "scheduled"),
        ("Interstellar",        "Hall 2",    "2026-06-17T15:00:00", 16.0,  "scheduled"),
        ("Interstellar",        "Hall VIP",  "2026-06-17T19:00:00", 35.0,  "scheduled"),
        ("The Matrix",          "Hall 3",    "2026-06-17T12:00:00", 12.0,  "scheduled"),
        ("Avengers: Endgame",   "Hall IMAX", "2026-06-18T14:00:00", 24.0,  "scheduled"),
        ("Avengers: Endgame",   "Hall 1",    "2026-06-18T20:00:00", 18.0,  "scheduled"),
        ("Joker",               "Hall 4",    "2026-06-18T17:00:00", 13.5,  "scheduled"),
        ("La La Land",          "Hall 2",    "2026-06-19T16:00:00", 11.0,  "scheduled"),
        ("Black Swan",          "Hall 4",    "2026-06-19T20:00:00", 12.0,  "scheduled"),
        ("Mad Max: Fury Road",  "Hall IMAX", "2026-06-20T15:00:00", 22.0,  "scheduled"),
        ("The Devil Wears Prada","Hall 3",   "2026-06-20T11:00:00", 10.0,  "scheduled"),
        ("Shutter Island",      "Hall 1",    "2026-06-20T19:00:00", 13.0,  "scheduled"),
        ("The Revenant",        "Hall IMAX", "2026-06-21T17:00:00", 23.0,  "scheduled"),
        ("Her",                 "Hall VIP",  "2026-06-21T20:00:00", 30.0,  "scheduled"),
    ]
    sessions = {}
    for title, hall_name, start_time, price, status in sessions_data:
        movie_id = movies.get(title)
        hall_id  = halls.get(hall_name)
        if movie_id and hall_id:
            s = post("/sessions/", {
                "movie_id": movie_id,
                "hall_id": hall_id,
                "start_time": start_time,
                "price": price,
                "status": status,
            })
            if s:
                sessions[f"{title}_{hall_name}"] = s["id"]

    print("\nSeed completed!")
    print(f"  Genres:   {len(genres)}")
    print(f"  Actors:   {len(actors)}")
    print(f"  Movies:   {len(movies)}")
    print(f"  Users:    {len(users)}")
    print(f"  Halls:    {len(halls)}")
    print(f"  Sessions: {len(sessions)}")


if __name__ == "__main__":
    main()
