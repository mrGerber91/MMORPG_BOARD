from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .views import CustomLoginView
from django.views.decorators.csrf import csrf_exempt
from django_ckeditor_5.views import upload_file
from bulletin_board.views import upload_file


urlpatterns = [
    path('register/', views.register, name='register'),
    path('advertisements/', views.advertisement_list, name='advertisement_list'),
    path('advertisements/<int:pk>/', views.advertisement_detail, name='advertisement_detail'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/responses/', views.response_list_view, name='response_list'),
    path('profile/responses/<int:response_id>/delete/', views.response_delete_view, name='response_delete'),
    path('profile/responses/<int:response_id>/accept/', views.response_accept_view, name='response_accept'),
    path('advertisements/<int:advertisement_pk>/add_response/', views.add_response, name='add_response'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('create_advertisement/', views.create_advertisement, name='create_advertisement'),
    path('edit/<int:pk>/', views.edit_advertisement, name='edit_advertisement'),
    path('confirm-registration/', views.confirm_registration, name='confirm_registration'),
    path('ckeditor5/image_upload/', csrf_exempt(upload_file), name='ckeditor5_upload'),


]
