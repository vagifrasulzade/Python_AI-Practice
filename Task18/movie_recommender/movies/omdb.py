import requests

from django.conf import settings

OMDB_URL = "https://www.omdbapi.com/"


def _request(params: dict) -> dict | None:
    api_key = settings.OMDB_API_KEY
    if not api_key:
        return None

    try:
        response = requests.get(
            OMDB_URL,
            params={"apikey": api_key, **params},
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()

        if data.get("Response") == "True":
            return data

    except requests.RequestException:
        pass

    return None


def get_movie_from_omdb(title: str) -> dict | None:
    return _request({"t": title, "plot": "full"})


def get_movie_by_imdb_id(imdb_id: str) -> dict | None:
    return _request({"i": imdb_id, "plot": "full"})


def search_omdb(term: str, page: int = 1) -> dict | None:
    """Search movies by keyword. Returns {"Search": [...], "totalResults": "..."}."""
    return _request({"s": term, "type": "movie", "page": page})