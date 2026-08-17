from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

import numpy as np

from .models import Movie


def recommend_movies(liked_movies, limit=12):
    movies = list(Movie.objects.all().order_by("id"))

    if not movies or not liked_movies:
        return []

    liked_ids = {movie.id for movie in liked_movies}

    texts = [
        f"{movie.description or ''} {movie.genre or ''}"
        for movie in movies
    ]

    vectorizer = TfidfVectorizer(
        stop_words="english",
        lowercase=True,
        ngram_range=(1, 2),
    )

    try:
        tfidf_matrix = vectorizer.fit_transform(texts)
    except ValueError:
        return []

    movie_index = {movie.id: index for index, movie in enumerate(movies)}
    liked_indexes = [
        movie_index[movie.id]
        for movie in liked_movies
        if movie.id in movie_index
    ]

    if not liked_indexes:
        return []

    user_profile = np.asarray(
        tfidf_matrix[liked_indexes].mean(axis=0)
    )
    similarities = cosine_similarity(
        user_profile, tfidf_matrix
    ).flatten()

    ranked = sorted(
        (
            (movie, float(similarities[index]))
            for index, movie in enumerate(movies)
            if movie.id not in liked_ids
        ),
        key=lambda item: item[1],
        reverse=True,
    )

    return [
        {
            "movie": movie,
            "score": round(score * 100, 1),
        }
        for movie, score in ranked[:limit]
    ]