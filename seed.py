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
    genres = {}
    for name in ["Action", "Drama", "Comedy", "Thriller", "Sci-Fi"]:
        g = post("/genres/", {"name": name})
        if g:
            genres[name] = g["id"]

    # --- Actors ---
    actors = {}
    for name in ["Tom Hanks", "Leonardo DiCaprio", "Scarlett Johansson", "Brad Pitt"]:
        a = post("/actors/", {
            "name": name,
            "bio": f"Bio of {name}",
            "age": 45,
            "gender": "male",
            "image_url": PLACEHOLDER_ACTOR,
        })
        if a:
            actors[name] = a["id"]

    # --- Movies ---
    movies = {}
    movies_data = [
        {
            "title": "Inception",
            "description": "A thief who steals corporate secrets through dream-sharing technology.",
            "duration": 148,
            "year": 2010,
            "rating": 8.8,
            "poster_url": PLACEHOLDER_POSTER,
            "actor_ids": [actors.get("Leonardo DiCaprio")],
            "genre_ids": [genres.get("Action"), genres.get("Sci-Fi")],
        },
        {
            "title": "Forrest Gump",
            "description": "The presidencies of Kennedy and Johnson through the eyes of Forrest Gump.",
            "duration": 142,
            "year": 1994,
            "rating": 8.8,
            "poster_url": PLACEHOLDER_POSTER,
            "actor_ids": [actors.get("Tom Hanks")],
            "genre_ids": [genres.get("Drama"), genres.get("Comedy")],
        },
        {
            "title": "Fight Club",
            "description": "An insomniac office worker forms an underground fight club.",
            "duration": 139,
            "year": 1999,
            "rating": 8.8,
            "poster_url": PLACEHOLDER_POSTER,
            "actor_ids": [actors.get("Brad Pitt")],
            "genre_ids": [genres.get("Drama"), genres.get("Thriller")],
        },
    ]
    for movie in movies_data:
        movie["actor_ids"] = [i for i in movie["actor_ids"] if i]
        movie["genre_ids"] = [i for i in movie["genre_ids"] if i]
        m = post("/movies/", movie)
        if m:
            movies[m["title"]] = m["id"]

    # --- Users ---
    users = {}
    for username, email in [("john_doe", "john@example.com"), ("jane_doe", "jane@example.com")]:
        u = post("/users/", {"username": username, "email": email, "password": "password123"})
        if u:
            users[username] = u["id"]

    # --- Halls ---
    halls = {}
    for name, capacity, hall_type in [("Hall 1", 100, "2D"), ("Hall 2", 80, "3D"), ("Hall IMAX", 150, "IMAX")]:
        h = post("/halls/", {"name": name, "capacity": capacity, "hall_type": hall_type})
        if h:
            halls[name] = h["id"]

    # --- Sessions ---
    sessions = {}
    sessions_data = [
        {"movie_id": movies.get("Inception"), "hall_id": halls.get("Hall 1"),    "start_time": "2026-06-15T14:00:00", "price": 12.5,  "status": "scheduled"},
        {"movie_id": movies.get("Forrest Gump"), "hall_id": halls.get("Hall 2"), "start_time": "2026-06-15T17:00:00", "price": 14.0,  "status": "scheduled"},
        {"movie_id": movies.get("Fight Club"), "hall_id": halls.get("Hall IMAX"),"start_time": "2026-06-15T20:00:00", "price": 18.0,  "status": "scheduled"},
    ]
    for s in sessions_data:
        if s["movie_id"] and s["hall_id"]:
            sess = post("/sessions/", s)
            if sess:
                sessions[sess["id"]] = sess["id"]

    print("\nSeed completed!")
    print(f"  Genres:   {len(genres)}")
    print(f"  Actors:   {len(actors)}")
    print(f"  Movies:   {len(movies)}")
    print(f"  Users:    {len(users)}")
    print(f"  Halls:    {len(halls)}")
    print(f"  Sessions: {len(sessions)}")


if __name__ == "__main__":
    main()
