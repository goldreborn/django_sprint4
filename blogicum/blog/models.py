from typing import Any
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth import get_user_model
from .validators import user_age, post_pub_time

User = get_user_model()

MAX_CHAR_LENGTH = 256


class AbstractModel(models.Model):

    is_published = models.BooleanField(
        default=True,
        verbose_name='Опубликовано',
        help_text='Снимите галочку, чтобы скрыть публикацию.'
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Добавлено'
    )

    class Meta:
        abstract = True


class Category(AbstractModel):

    title = models.CharField(
        max_length=MAX_CHAR_LENGTH,
        verbose_name='Заголовок'
    )

    description = models.TextField(
        verbose_name='Описание')

    slug = models.SlugField(
        unique=True,
        verbose_name='Идентификатор',
        help_text='Идентификатор страницы для URL; '
        'разрешены символы латиницы, цифры, дефис и подчёркивание.'
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'

    def __str__(self) -> str:
        return self.title

class Tag(models.Model):

    tag = models.CharField('Тег', max_length=20)

    def __str__(self):
        return self.tag


class Location(AbstractModel):

    name = models.CharField(
        max_length=MAX_CHAR_LENGTH,
        verbose_name='Название места'
    )

    class Meta:
        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'

    def __str__(self) -> str:
        return self.name

class Profile(AbstractUser):

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
    username = models.CharField(
        max_length=MAX_CHAR_LENGTH,
        verbose_name='юзернэйм',
    )

    is_staff = models.BooleanField(
        default=False,
        verbose_name='Суперпользователь',
    )

    date_joined = models.DateTimeField()

class Post(AbstractModel):

    title = models.CharField(
        max_length=MAX_CHAR_LENGTH,
        verbose_name='Заголовок'
    )

    text = models.TextField(
        verbose_name='Текст')

    pub_date = models.DateTimeField(
        verbose_name='Дата и время публикации',
        validators = (post_pub_time,),
        help_text='Если установить дату и время в будущем '
                  '— можно делать отложенные публикации.')

    author = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор публикации'
    )

    location = models.ForeignKey(
        Location,
        verbose_name='Местоположение',
        related_name='posts',
        on_delete=models.SET_NULL,
        null=True,
    )

    category = models.ForeignKey(
        Category,
        verbose_name='Категория',
        related_name='posts',
        on_delete=models.SET_NULL,
        null=True,
    )

    class Meta:
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'
        ordering = ['-pub_date']

    def __str__(self) -> str:
        return self.title