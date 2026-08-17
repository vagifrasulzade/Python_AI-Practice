from django.db import models


class Movie(models.Model):
    title = models.CharField(max_length=255, unique=True)
    description = models.TextField()
    image_url = models.URLField(max_length=1000, blank=True)
    poster_url = models.URLField(max_length=1000, blank=True)
    year = models.CharField(max_length=20, blank=True)
    genre = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.title

    @property
    def display_image(self):
        return self.poster_url or self.image_url