import csv
import os

from django.core.management.base import BaseCommand

from reviews.models import (Category, Comment, CustomUser, Genre, GenreTitle,
                            Review, Title)

STATIC_URL = "static/data/"
TABLES_DICT = {
    CustomUser: 'users.csv',
    Category: 'category.csv',
    Genre: 'genre.csv',
    Title: 'titles.csv',
    Review: 'review.csv',
    Comment: 'comments.csv',
    GenreTitle: 'genre_title.csv'
}


class Command(BaseCommand):
    help = 'Load data from CSV files into database'

    def handle(self, *args, **options):
        for model_class, file_name in TABLES_DICT.items():
            csv_file_path = os.path.join(STATIC_URL, file_name)
            with open(csv_file_path, 'r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    model_instance = model_class()
                    for field_name, value in row.items():
                        try:
                            if hasattr(model_class, field_name):
                                setattr(model_instance, field_name, value)
                        except Exception as error:
                            print(f'Error in row {row.get("id")}.\n'
                                  f'Error text - {error}')
                    model_instance.save()

        self.stdout.write(self.style.SUCCESS('Data loaded successfully'))
