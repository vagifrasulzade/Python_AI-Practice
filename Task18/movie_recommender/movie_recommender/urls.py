"""
URL configuration for movie_recommender project.
"""
from django.urls import include, path

urlpatterns = [
    path("", include("movies.urls")),
]