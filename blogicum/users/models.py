from django.db import models
from django.contrib.auth.models import AbstractUser
from blog.validators import user_age
from django.utils.translation import gettext_lazy

# Create your models here.
class Profile(AbstractUser):
    username = None

    first_name = models.CharField('Имя', max_length=20)
    last_name = models.CharField(
        'Фамилия', blank=True, help_text='Необязательное поле', max_length=20
    )
    birthday = models.DateField('Дата рождения', validators=(user_age,))
    image = models.ImageField('Фото', upload_to='profiles_images', blank=True)
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Теги',
        blank=True,
        help_text='Удерживайте Ctrl для выбора нескольких вариантов'
    )
    
    email = models.EmailField(gettext_lazy("email address"), unique=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    is_staff = models.BooleanField(
        default=False,
        verbose_name='Суперпользователь',
    )

    date_joined = models.DateTimeField()