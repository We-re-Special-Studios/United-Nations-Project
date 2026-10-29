from django.contrib import admin
from ..models import Company

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    autocomplete_fields = ['headquarters']