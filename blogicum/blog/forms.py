from django import forms
from django.core.mail import send_mail

from .models import Post, Comment


class CommentForm(forms.ModelForm):

    ...

    class Meta:

        model = Comment

        fields = ('text',)

        widgets = {
            'created_at': forms.DateInput(attrs={'type': 'date'}),
            'text': forms.Textarea(attrs={'rows': 3}),
        }


class PostForm(forms.ModelForm):

    def clean(self):
        super().clean()

        send_mail(
            subject='Email',
            message='Найден баг',
            from_email='post_form@acme.not',
            recipient_list=['admin@acme.not'],
            fail_silently=True,
        )

    class Meta:

        model = Post

        exclude = ('author', 'comment_count')

        widgets = {
            'pub_date': forms.DateInput(attrs={'type': 'date'}),
            'text': forms.Textarea(attrs={'rows': 3}),
        }
