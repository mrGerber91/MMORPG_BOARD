from django.contrib import admin
from django.urls import path, include
from bulletin_board.views import home, logout_view
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('register/', include('bulletin_board.urls')),
    path('logout/', logout_view, name='logout'),
    path('', include('bulletin_board.urls')),
    path('', home, name='home'),
    path("ckeditor5/", include('django_ckeditor_5.urls'), name="ck_editor_5_upload_file"),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
