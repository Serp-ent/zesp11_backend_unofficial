from django.contrib import admin

from backend.gotale.models import Location

# Register your models here.


@admin.register(Location)
class AdminLocation(admin.ModelAdmin):
    pass
