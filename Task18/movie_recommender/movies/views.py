from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .models import Movie
from .recommendation import recommend_movies

LIKED_KEY = "liked_movie_ids"


def _liked_ids(request):
    return set(request.session.get(LIKED_KEY, []))


def movie_list(request):
    movies = Movie.objects.all().order_by("title")
    query = request.GET.get("q", "").strip()

    if query:
        movies = movies.filter(
            Q(title__icontains=query)
            | Q(description__icontains=query)
            | Q(genre__icontains=query)
        )

    liked_ids = _liked_ids(request)

    return render(
        request,
        "movies/movie_list.html",
        {
            "movies": movies,
            "liked_ids": liked_ids,
            "query": query,
        },
    )


@require_POST
def toggle_like(request, movie_id):
    get_object_or_404(Movie, id=movie_id)

    liked_ids = _liked_ids(request)

    if movie_id in liked_ids:
        liked_ids.discard(movie_id)
    else:
        liked_ids.add(movie_id)

    request.session[LIKED_KEY] = list(liked_ids)

    next_url = request.POST.get("next")
    return redirect(next_url or "movie_list")


def liked_movies(request):
    liked_ids = _liked_ids(request)
    movies = Movie.objects.filter(id__in=liked_ids).order_by("title")

    return render(
        request,
        "movies/liked_movies.html",
        {
            "movies": movies,
            "liked_ids": liked_ids,
        },
    )


def recommendations(request):
    liked_ids = _liked_ids(request)
    liked_movies = list(Movie.objects.filter(id__in=liked_ids))

    recommendations_data = recommend_movies(liked_movies)

    return render(
        request,
        "movies/recommendations.html",
        {"recommendations": recommendations_data},
    )