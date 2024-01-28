# Generated by Django 3.2.16 on 2024-01-27 12:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0002_auto_20240127_1436'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='tags',
            field=models.ManyToManyField(blank=True, help_text='Удерживайте Ctrl для выбора нескольких вариантов', to='blog.Tag', verbose_name='Теги'),
        ),
        migrations.DeleteModel(
            name='Profile',
        ),
    ]
