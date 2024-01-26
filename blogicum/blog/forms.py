# birthday/forms.py
from django import forms

# Импортируем класс модели Birthday.
from .models import Profile
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

User = get_user_model()

class ProfileForm(forms.ModelForm):

    ...

    class Meta:

        model = User

        fields = '__all__'
        exclude = ('password', )

        widgets = {
            'age': '',
            'age': '',
        }