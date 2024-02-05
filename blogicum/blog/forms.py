from django import forms
from django.core.mail import send_mail

from .models import Post, Comment


class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ('text',)
        widgets = {
            'text': forms.Textarea(attrs={'rows': 3}),
        }


class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        exclude = ('author', 'comment_count')
        widgets = {
            'pub_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'text': forms.Textarea(attrs={'rows': 3}),
        }
