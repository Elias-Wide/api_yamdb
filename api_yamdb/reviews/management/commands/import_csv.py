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

    def create_correct_row_fields(self, row):
        try:
            if row.get('author'):
                row['author'] = CustomUser.objects.get(pk=row['author'])
            if row.get('review_id'):
                row['review'] = Review.objects.get(pk=row['review_id'])
            if row.get('title_id'):
                row['title'] = Title.objects.get(pk=row['title_id'])
            if row.get('category'):
                row['category'] = Category.objects.get(pk=row['category'])
            if row.get('genre'):
                row['genre'] = Genre.objects.get(pk=row['genre'])
        except Exception as error:
            print(f'Error in row {row.get("id")}.'
                  f'Error text - {error}')
        return row

    def handle(self, *args, **options):
        for model_class, file_name in TABLES_DICT.items():
            csv_file_path = os.path.join(STATIC_URL, file_name)
            with open(csv_file_path, 'r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    row = self.create_correct_row_fields(row)
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
