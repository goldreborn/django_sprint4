from django.contrib import admin

from .models import Location, Post, Category


admin.site.register(Location)
admin.site.register(Post)
admin.site.register(Category)
