import requests

from django.conf import settings


def get_movie_from_omdb(title: str) -> dict | None:
    api_key = settings.OMDB_API_KEY
    if not api_key:
        return None

    try:
        response = requests.get(
            "https://www.omdbapi.com/",
            params={
                "apikey": api_key,
                "t": title,
                "plot": "full",
            },
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()

        if data.get("Response") == "True":
            return data

    except requests.RequestException:
        pass

    return None