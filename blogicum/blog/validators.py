from datetime import date
from django.core.exceptions import ValidationError

today = date.today()


def user_age(age: date) -> None:
    user_age = (today - age).days / 365
    if user_age < 1 or user_age > 120:
        raise ValidationError(
            'Ожидается возраст от 1 года до 120 лет'
        )


def post_pub_time(pub):
    if pub.date() > today:
        raise ValidationError(
            'Пост из будущего не может быть опубликован'
        )

