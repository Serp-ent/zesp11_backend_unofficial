from django.contrib import admin

from gotale.models import Location

# Register your models here.


@admin.register(Location)
class AdminLocation(admin.ModelAdmin):
    pass
