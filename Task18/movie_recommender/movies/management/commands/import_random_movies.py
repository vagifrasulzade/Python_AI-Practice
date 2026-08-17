import math
import random

from django.core.management.base import BaseCommand

from movies.models import Movie
from movies.omdb import get_movie_by_imdb_id, search_omdb

# OMDb-nin random endpoint-i yoxdur, ona gore random acar sozle axtaris edirik
KEYWORDS = [
    "love", "war", "space", "city", "night", "blood", "dream", "king",
    "shadow", "fire", "star", "ghost", "island", "road", "storm", "silent",
    "last", "dark", "summer", "winter", "girl", "boy", "man", "woman",
    "house", "train", "river", "moon", "sun", "game", "hunt", "escape",
    "secret", "lost", "wild", "heart", "iron", "gold", "stone", "rain",
]

# OMDb `s=` sorgusu max 100 sehife qaytarir
MAX_PAGE = 100


class Command(BaseCommand):
    help = "Import random movies from OMDb using random keyword searches"

    def add_arguments(self, parser):
        parser.add_argument(
            "--count",
            type=int,
            default=60,
            help="Nece film import edilsin (default: 60)",
        )
        parser.add_argument(
            "--seed",
            type=int,
            default=None,
            help="Random seed — eyni neticeni tekrarlamaq ucun",
        )

    def handle(self, *args, **options):
        count = options["count"]
        seed = options["seed"]

        if seed is not None:
            random.seed(seed)

        candidates = self._collect_candidates(count)

        if not candidates:
            self.stderr.write(
                self.style.ERROR(
                    "OMDb-den hec bir netice gelmedi. "
                    "OMDB_API_KEY duzgundur mu?"
                )
            )
            return

        created_count = 0
        updated_count = 0
        skipped = 0

        for imdb_id in list(candidates)[:count]:
            data = get_movie_by_imdb_id(imdb_id)

            if not data:
                skipped += 1
                continue

            title = data.get("Title", "").strip()
            plot = data.get("Plot", "").strip()

            if not title or plot in ("", "N/A"):
                skipped += 1
                continue

            defaults = {"description": plot}

            poster = data.get("Poster", "")
            if poster and poster != "N/A":
                defaults["poster_url"] = poster

            year = data.get("Year", "")
            if year and year != "N/A":
                defaults["year"] = year

            genre = data.get("Genre", "")
            if genre and genre != "N/A":
                defaults["genre"] = genre

            _, created = Movie.objects.update_or_create(
                title=title,
                defaults=defaults,
            )

            if created:
                created_count += 1
            else:
                updated_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Random import bitdi. Yaradildi: {created_count}, "
                f"Yenilendi: {updated_count}, Atlandi: {skipped}"
            )
        )

    def _collect_candidates(self, count):
        """Random acar sozlerle axtarib unikal imdbID toplusu yigir."""
        imdb_ids = []
        seen = set()

        keywords = random.sample(KEYWORDS, len(KEYWORDS))

        for keyword in keywords:
            if len(imdb_ids) >= count:
                break

            first_page = search_omdb(keyword)

            if not first_page:
                continue

            results = first_page.get("Search", [])

            total = int(first_page.get("totalResults", "0") or 0)
            max_page = min(math.ceil(total / 10), MAX_PAGE)

            if max_page > 1:
                page = random.randint(1, max_page)
                if page > 1:
                    other_page = search_omdb(keyword, page=page)
                    if other_page:
                        results = other_page.get("Search", results)

            random.shuffle(results)

            for item in results:
                imdb_id = item.get("imdbID")

                if not imdb_id or imdb_id in seen:
                    continue

                seen.add(imdb_id)
                imdb_ids.append(imdb_id)

                self.stdout.write(
                    f"  [{keyword}] {item.get('Title', '?')} "
                    f"({item.get('Year', '?')})"
                )

                if len(imdb_ids) >= count:
                    break

        return imdb_ids
