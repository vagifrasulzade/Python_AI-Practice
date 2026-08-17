from pathlib import Path

import pandas as pd
from django.conf import settings
from django.core.management.base import BaseCommand

from movies.models import Movie
from movies.omdb import get_movie_from_omdb

MOVIE_LIMIT = 60


class Command(BaseCommand):
    help = "Import 60 movies from real_movies_sample.xlsx with OMDb posters"

    def handle(self, *args, **options):
        excel_path = Path(settings.BASE_DIR) / "real_movies_sample.xlsx"

        if not excel_path.exists():
            self.stderr.write(
                self.style.ERROR(
                    f"Excel file not found: {excel_path}"
                )
            )
            return

        df = pd.read_excel(excel_path).head(MOVIE_LIMIT)

        required_columns = {"Title", "Description", "ImageUrl"}
        missing = required_columns - set(df.columns)

        if missing:
            self.stderr.write(
                self.style.ERROR(
                    f"Missing Excel columns: {', '.join(sorted(missing))}"
                )
            )
            return

        created_count = 0
        updated_count = 0
        omdb_found = 0

        for _, row in df.iterrows():
            title = str(row["Title"]).strip()
            description = str(row["Description"]).strip()
            image_url = (
                ""
                if pd.isna(row["ImageUrl"])
                else str(row["ImageUrl"]).strip()
            )

            defaults = {
                "description": description,
                "image_url": image_url,
            }

            omdb = get_movie_from_omdb(title)
            if omdb:
                poster = omdb.get("Poster", "")
                if poster and poster != "N/A":
                    defaults["poster_url"] = poster
                    omdb_found += 1

                year = omdb.get("Year", "")
                if year and year != "N/A":
                    defaults["year"] = year

                genre = omdb.get("Genre", "")
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
                f"Import finished. Created: {created_count}, "
                f"Updated: {updated_count}, OMDb posters: {omdb_found}"
            )
        )