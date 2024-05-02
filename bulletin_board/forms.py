from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from .models import Advertisement
from django.urls import reverse_lazy
from django_ckeditor_5.widgets import CKEditor5Widget
from .models import Response


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    def clean_email(self):
        email = self.cleaned_data.get('email')
        try:
            validate_email(email)
        except ValidationError:
            raise forms.ValidationError("Некорректный адрес электронной почты.")
        return email

    class Meta:
        model = User
        fields = ('username', 'email')

class ResponseForm(forms.ModelForm):
    class Meta:
        model = Response
        fields = ['text']

class ResponseFilterForm(forms.Form):
    user_id = forms.ModelChoiceField(label='Пользователь', queryset=User.objects.all(), required=False)
    category_choices = [('', 'Все')] + Advertisement.category_choices
    category = forms.ChoiceField(label='Категория', choices=category_choices, required=False)

class AdvertisementForm(forms.ModelForm):
    class Meta:
        model = Advertisement
        fields = ['title', 'text', 'category',]
        widgets = {
            "text": CKEditor5Widget(
                attrs={"class": "django_ckeditor_5"},
                config_name="extends"
            )
        }

class ConfirmationCodeForm(forms.Form):
    confirmation_code = forms.CharField(max_length=8, label='Код подтверждения')



