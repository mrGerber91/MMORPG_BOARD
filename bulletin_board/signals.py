from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import Response
from django.template.loader import render_to_string
from django.contrib.auth.models import User
from .models import Advertisement
from django.core.mail import EmailMultiAlternatives

@receiver(post_save, sender=Response)
def send_response_notification(sender, instance, created, **kwargs):
    if created:
        subject = 'Новый отклик на ваше объявление'
        message = f'Пользователь {instance.user.username} оставил отклик на ваше объявление "{instance.advertisement.title}".'
        recipient_list = [instance.advertisement.created_by.email]
        send_mail(subject, message, settings.EMAIL_HOST_USER, recipient_list)
    elif instance.accepted:
        subject = 'Ваш отклик принят'
        message = f'Ваш отклик на объявление "{instance.advertisement.title}" был принят.'
        recipient_list = [instance.user.email]
        send_mail(subject, message, settings.EMAIL_HOST_USER, recipient_list)

@receiver(post_save, sender=Advertisement)
def send_new_advertisement_notification(sender, instance, created, **kwargs):
    if created:
        users_to_notify = User.objects.exclude(id=instance.created_by.id)
        for user in users_to_notify:
            subject = 'Новое объявление на нашем сайте!'
            text_content = 'Новое объявление на нашем сайте!'
            html_content = render_to_string('new_advertisement_notification.html', {'advertisement': instance})
            msg = EmailMultiAlternatives(subject, text_content, settings.EMAIL_HOST_USER, [user.email])
            msg.attach_alternative(html_content, "text/html")
            msg.send()