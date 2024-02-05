from django import forms

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
        exclude = ('author',)
        widgets = {
            'pub_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'text': forms.Textarea(attrs={'rows': 3}),
        }
