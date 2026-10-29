from django.contrib import admin
from ..models import Territory

@admin.register(Territory)
class TerritoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)  # 🔍 enables the search bar
    ordering = ('name',)