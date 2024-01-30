from django.contrib import admin

from .models import Location, Post, Category, Comment, Tag


admin.site.register(Location)
admin.site.register(Post)
admin.site.register(Category)
admin.site.register(Comment)
admin.site.register(Tag)
