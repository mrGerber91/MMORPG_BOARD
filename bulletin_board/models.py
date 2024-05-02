from django.db import models
from django.contrib.auth.models import User
import secrets
from django.urls import reverse
from django_ckeditor_5.fields import CKEditor5Field

class Advertisement(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField('Title', max_length=200)
    text = CKEditor5Field('Text', config_name='extends')
    category_choices = [
        ('Танки', 'Танки'),
        ('Хилы', 'Хилы'),
        ('ДД', 'ДД'),
        ('Торговцы', 'Торговцы'),
        ('Гилдмастеры', 'Гилдмастеры'),
        ('Квестгиверы', 'Квестгиверы'),
        ('Кузнецы', 'Кузнецы'),
        ('Кожевники', 'Кожевники'),
        ('Зельевары', 'Зельевары'),
        ('Мастера заклинаний', 'Мастера заклинаний')
    ]
    category = models.CharField('Category', max_length=100, choices=category_choices)
    created_at = models.DateTimeField('Created at', auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='advertisements_created')
    last_modified_at = models.DateTimeField('Last modified at', auto_now=True)
    last_modified_by = models.ForeignKey(User, related_name='modified_ads', on_delete=models.SET_NULL, null=True)

    def get_absolute_url(self):
        return reverse('advertisement_detail', args=[str(self.id)])

    def save(self, *args, **kwargs):
        if not self.id:
            self.created_by = self.user
        super().save(*args, **kwargs)

class Response(models.Model):
    advertisement = models.ForeignKey(Advertisement, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField('Text')
    accepted = models.BooleanField('Accepted', default=False)


class ConfirmationCode(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=8)
    confirmed = models.BooleanField(default=False)

    def __str__(self):
        return f"Confirmation code for {self.user.username}"


