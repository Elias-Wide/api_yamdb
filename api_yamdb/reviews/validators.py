import datetime as dt


def validate_year(year):
    if year > dt.date.today().year:
        raise ValueError(f'Incorrect year {year}')
