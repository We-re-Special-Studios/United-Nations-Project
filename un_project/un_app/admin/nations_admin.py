from django.contrib import admin
from ..models import Nation

@admin.register(Nation)
class NationAdmin(admin.ModelAdmin):
    search_fields = ['name']