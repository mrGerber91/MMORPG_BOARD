from django.shortcuts import render, redirect, get_object_or_404
from .forms import CustomUserCreationForm, ResponseFilterForm, AdvertisementForm, ConfirmationCodeForm
from .models import Advertisement, Response
from .forms import ResponseForm
from django.contrib.auth import logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.http import HttpResponse
from .models import ConfirmationCode
from django.core.mail import send_mail
from django.contrib.auth.views import LoginView
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse_lazy
import random
import string
import os
from django.conf import settings

def home(request):
    return render(request, 'home.html')


def generate_confirmation_code(length=8):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # Сначала отключаем аккаунт пользователя
            user.save()

            # Генерируем код подтверждения
            confirmation_code = generate_confirmation_code()
            # Создаем объект ConfirmationCode и связываем его с только что созданным пользователем
            confirmation_code_obj = ConfirmationCode.objects.create(user=user, code=confirmation_code)

            # Отправляем код подтверждения по электронной почте
            send_confirmation_email(user.email, confirmation_code)

            # Сохраняем адрес электронной почты пользователя в сессии
            request.session['user_email'] = user.email

            return redirect('confirm_registration')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

def confirm_registration(request):
    if request.method == 'POST':
        form = ConfirmationCodeForm(request.POST)
        if form.is_valid():
            confirmation_code = form.cleaned_data['confirmation_code']
            # Получаем адрес электронной почты пользователя из сессии
            user_email = request.session.get('user_email')
            if user_email:
                try:
                    # Получаем только что созданного пользователя по адресу электронной почты
                    user = User.objects.get(email=user_email)
                    # Получаем объект ConfirmationCode для только что созданного пользователя
                    confirmation_code_obj = ConfirmationCode.objects.get(user=user)
                    # Проверяем, совпадает ли введенный пользователем код с кодом в базе данных
                    if confirmation_code == confirmation_code_obj.code and not confirmation_code_obj.confirmed:
                        # Если код совпадает и еще не подтвержден, подтверждаем регистрацию
                        confirmation_code_obj.confirmed = True
                        confirmation_code_obj.save()
                        # Активируем аккаунт пользователя
                        user.is_active = True
                        user.save()
                        messages.success(request, 'Регистрация успешно завершена. Теперь вы можете войти в систему.')
                        return redirect('login')  # Перенаправляем на страницу входа
                    else:
                        # Если код неверный или уже подтвержден, выводим ошибку
                        messages.error(request, 'Неверный код подтверждения или уже подтвержден.')
                except User.DoesNotExist:
                    # Если пользователь с таким адресом электронной почты не найден, выводим ошибку
                    messages.error(request, 'Пользователь с таким адресом электронной почты не найден.')
                except ConfirmationCode.DoesNotExist:
                    # Если объект ConfirmationCode не найден, выводим ошибку
                    messages.error(request, 'Для вас не найден код подтверждения.')
            else:
                # Если адрес электронной почты пользователя не найден в сессии, выводим ошибку
                messages.error(request, 'Адрес электронной почты пользователя не найден.')
        else:
            # Если форма невалидна, выводим ошибку
            messages.error(request, 'Форма невалидна.')
    else:
        form = ConfirmationCodeForm()
    return render(request, 'registration/confirm_registration.html', {'form': form})

def send_confirmation_email(email, code):
    send_mail(
        'Подтверждение регистрации',
        f'Ваш код подтверждения регистрации: {code}',
        'user7seven@yandex.ru',  # замените на ваш email для отправки
        [email],
        fail_silently=False,
    )


def logout_view(request):
    if request.method == 'GET':
        logout(request)
        return redirect('home')

def advertisement_list(request):
    advertisements = Advertisement.objects.all()
    return render(request, 'advertisement_list.html', {'advertisements': advertisements})

def advertisement_detail(request, pk):
    advertisement = get_object_or_404(Advertisement, pk=pk)
    return render(request, 'advertisement_detail.html', {'advertisement': advertisement})

def profile_view(request):
    return render(request, 'profile.html')

def response_list_view(request):
    responses = Response.objects.all()
    form = ResponseFilterForm(request.GET)
    if form.is_valid():
        user_id = form.cleaned_data.get('user_id')
        category = form.cleaned_data.get('category')
        if user_id:
            responses = responses.filter(user_id=user_id)
        if category:
            responses = responses.filter(advertisement__category=category)
    if not request.user.is_superuser:
        responses = responses.filter(advertisement__user=request.user)
    return render(request, 'response_list.html', {'responses': responses, 'form': form})

def response_delete_view(request, response_id):
    response = get_object_or_404(Response, pk=response_id)
    if request.method == 'POST':
        response.delete()
        messages.success(request, 'Отклик успешно удален.')
    return redirect('response_list')

def response_accept_view(request, response_id):
    response = get_object_or_404(Response, pk=response_id)
    if request.method == 'POST':
        response.accepted = True
        response.save()
        # Логика для отправки уведомления пользователю, оставившему отклик
        messages.success(request, 'Отклик успешно принят.')
    return redirect('response_list')


def add_response(request, advertisement_pk):
    advertisement = get_object_or_404(Advertisement, pk=advertisement_pk)

    advertisements_exclude_user = Advertisement.objects.exclude(user=request.user)

    if request.method == 'POST':
        form = ResponseForm(request.POST)
        if form.is_valid():
            response = form.save(commit=False)
            response.advertisement = advertisement
            response.user = request.user
            response.save()
            return redirect('advertisement_detail', pk=advertisement_pk)
    else:
        form = ResponseForm()
    return render(request, 'add_response.html', {'form': form, 'advertisement': advertisement})

@login_required
def create_advertisement(request):
    if request.method == 'POST':
        form = AdvertisementForm(request.POST)
        if form.is_valid():
            advertisement = form.save(commit=False)
            advertisement.user = request.user
            advertisement.save()
            return redirect('advertisement_list')
    else:
        form = AdvertisementForm()
    return render(request, 'create_advertisement.html', {'form': form})

@login_required
def edit_advertisement(request, pk):
    advertisement = get_object_or_404(Advertisement, pk=pk)
    if request.method == 'POST':
        form = AdvertisementForm(request.POST, instance=advertisement)
        if form.is_valid():
            advertisement = form.save(commit=False)
            advertisement.last_modified_by = request.user
            advertisement.save()
            messages.success(request, 'Объявление успешно отредактировано.')
            return redirect('advertisement_list')
    else:
        form = AdvertisementForm(instance=advertisement)
    return render(request, 'edit_advertisement.html', {'form': form})

class CustomLoginView(LoginView):
    def dispatch(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect('home')  # Пользователь уже вошел в систему, перенаправляем на главную страницу
        return super().dispatch(*args, **kwargs)

    def form_valid(self, form):
        user = form.get_user()
        if user.is_active:
            return super().form_valid(form)
        else:
            messages.error(self.request, 'Ваш аккаунт не активирован. Пожалуйста, подтвердите регистрацию.')
            return redirect('login')

@csrf_exempt
def upload_file(request):
    if request.method == 'POST' and request.FILES.get('upload'):
        uploaded_file = request.FILES['upload']
        # Формируем путь для сохранения файла в корневую папку media
        file_path = os.path.join(settings.MEDIA_ROOT, uploaded_file.name)
        # Открываем файл для записи в бинарном режиме
        with open(file_path, 'wb') as destination:
            # Записываем содержимое загруженного файла в файл на сервере
            for chunk in uploaded_file.chunks():
                destination.write(chunk)
        # Формируем URL для доступа к загруженному файлу
        file_url = os.path.join(settings.MEDIA_URL, uploaded_file.name)
        return JsonResponse({'url': file_url})
    else:
        return JsonResponse({'error': 'Invalid request'})

