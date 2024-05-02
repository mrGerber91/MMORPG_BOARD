from django.contrib import admin
from .models import Advertisement
from .forms import AdvertisementForm
from .models import Response


class AdvertisementAdmin(admin.ModelAdmin):
    form = AdvertisementForm


class ResponseAdmin(admin.ModelAdmin):
    list_display = ('user', 'text')


admin.site.register(Response, ResponseAdmin)
admin.site.register(Advertisement, AdvertisementAdmin)
