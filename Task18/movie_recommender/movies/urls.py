from django.urls import path

from . import views

urlpatterns = [
    path("", views.movie_list, name="movie_list"),
    path("liked/", views.liked_movies, name="liked_movies"),
    path("recommendations/", views.recommendations, name="recommendations"),
    path("movies/<int:movie_id>/like/", views.toggle_like, name="toggle_like"),
]