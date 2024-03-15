import csv
import os

from django.core.management.base import BaseCommand

from reviews.models import (Category, Comment, User, Genre, GenreTitle,
                            Review, Title)

STATIC_URL = "static/data/"
TABLES_DICT = {
    User: 'users.csv',
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
            row_list = []
            with open(csv_file_path, 'r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    try:
                        if file_name == 'titles.csv':
                            row['category'] = Category(int(row['category']))
                        elif file_name == 'review.csv':
                            row['author'] = User(int(row['author']))
                        elif file_name == 'comments.csv':
                            row['author'] = User(int(row['author']))
                        row_list.append(model_class(**row))
                    except Exception as error:
                        self.stdout.write(f'Error in row {row.get("id")}.'
                                          f' Error text - {error}')
                model_class.objects.bulk_create(row_list)

        self.stdout.write(self.style.SUCCESS('Data loaded successfully'))
