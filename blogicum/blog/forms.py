from django import forms

from .models import Post, Comment

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

        widgets = {
            'pub_date': forms.DateInput(attrs={'type': 'date'}),
            'tags': forms.Textarea()
        }

