# birthday/forms.py
from django import forms

# Импортируем класс модели Birthday.
from .models import Profile, Post, Comment

class CommentForm(forms.ModelForm):

    ...

    class Meta:
        
        model = Comment

        fields = ('text',)


class PostForm(forms.ModelForm):

    def clean(self):

        super().clean()

    class Meta:

        model = Post

        fields = '__all__'

