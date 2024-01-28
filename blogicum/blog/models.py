from django.db import models
from .validators import post_pub_time
from django.contrib.auth import get_user_model
from django.urls import reverse

MAX_CHAR_LENGTH = 256

User = get_user_model()


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

    def get_absolute_url(self):
        return reverse("blog:category_posts", kwargs={'slug': self.slug})

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


class Post(AbstractModel):

    title = models.CharField(
        max_length=MAX_CHAR_LENGTH,
        verbose_name='Заголовок'
    )

    text = models.TextField(
        verbose_name='Текст')

    pub_date = models.DateTimeField(
        verbose_name='Дата и время публикации',
        validators=(post_pub_time,),
        help_text='Если установить дату и время в будущем '
                  '— можно делать отложенные публикации.')

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор публикации'
    )

    tags = models.ManyToManyField(
        Tag,
        verbose_name='Теги',
        blank=True,
        help_text='Удерживайте Ctrl для выбора нескольких вариантов'
    )

    location = models.ForeignKey(
        Location,
        verbose_name='Местоположение',
        related_name='posts',
        on_delete=models.SET_NULL,
        null=True,
    )

    image = models.ImageField('Фото', upload_to='posts_images', blank=True)

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

    def get_absolute_url(self):
        return reverse('blog:detail', kwargs={'pk': self.pk}) 

    def __str__(self) -> str:
        return self.title


class Comment(models.Model):
    text = models.TextField('Напишите комментарий')
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comment',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        ordering = ('created_at',)
