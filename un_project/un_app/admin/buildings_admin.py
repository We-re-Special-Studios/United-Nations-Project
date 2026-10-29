from django.contrib import admin, messages
from ..models import Building, PartialBuildingOwnership
from django.utils.html import format_html
from django import forms
from django.db.models import Count
from django.core.exceptions import ValidationError

class BuildingAdminForm(forms.ModelForm):
    class Meta:
        model = Building
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()

        territory = cleaned_data.get('territory')
        builders = cleaned_data.get('main_builders')

        warnings = []

        if not territory:
            warnings.append("Territory is not assigned.")

        if not builders:
            warnings.append("No main builders assigned.")

        self.warning_messages = warnings

        return cleaned_data


class MissingInfoFilter(admin.SimpleListFilter):
    title = "missing info"
    parameter_name = "missing_info"

    def lookups(self, request, model_admin):
        return (
            ("missing_territory", "Missing Territory"),
            ("missing_builders", "Missing Builders"),
        )

    def queryset(self, request, queryset):
        queryset = queryset.annotate(builder_count=Count("main_builders"))

        if self.value() == "missing_territory":
            return queryset.filter(territory__isnull=True)

        if self.value() == "missing_builders":
            return queryset.filter(builder_count=0)

        return queryset
    
    
class PartialBuildingOwnershipInline(admin.TabularInline):
    model = PartialBuildingOwnership
    extra = 1

    def clean(self):
        super().clean()

        total = 0

        for form in self.forms:
            if hasattr(form, 'cleaned_data'):
                data = form.cleaned_data

                if data and not data.get('DELETE', False):
                    total += data.get('percentage', 0)

        if total > 100:
            raise ValidationError(
                "Partial ownership cannot exceed 100%."
            )
    

@admin.register(Building)
class BuildingAdmin(admin.ModelAdmin):
    form = BuildingAdminForm
    
    inlines = [
        PartialBuildingOwnershipInline,
    ]
    
    autocomplete_fields = ('territory',)
    
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

        warnings = getattr(form, 'warning_messages', [])

        for warning in warnings:
            self.message_user(request, warning, level=messages.WARNING)
    
    @admin.display(description='Warnings')
    def missing_info(self, obj):
        warnings = []

        if not obj.territory:
            warnings.append("⚠ Territory")

        if not obj.main_builders.exists():
            warnings.append("⚠ Builders")

        return " | ".join(warnings) if warnings else "✓"

    # Columns shown in the list view
    list_display = (
        'name_display',
        'owner',
        'territory',
        'height',
        'year_started',
        'year_destroyed',
        'coordinates',
        'completed',
        'missing_info',
    )
    
    search_fields = (
        'name',
        'owner__name',
        'owner__abbreviation',
        'territory__name',
        'x_coordinate',
        'z_coordinate',
        'architectural_style',
        'main_builders__username',
    )

    list_filter = (
        'owner',
        'completed',
        MissingInfoFilter,
        'historic_site',
        'architectural_genius',
        'mopq_award',
        'year_destroyed',  # allows filtering destroyed vs existing
    )

    ordering = ('name',)

    filter_horizontal = ('main_builders',)

    # -----------------------------------------
    # Custom Name Display (Strikethrough if destroyed)
    # -----------------------------------------
    @admin.display(description="Name", ordering="name")
    def name_display(self, obj):
        if obj.year_destroyed:
            return format_html(
                "<span style='text-decoration: line-through; color: #999;'>{}</span>",
                obj.name
            )
        return obj.name

    # -----------------------------------------
    # Optional: Show destroyed buildings in admin
    # even if you made a default manager filtering them out
    # -----------------------------------------
    def get_queryset(self, request):
        # Use all_objects if you implemented soft-delete manager
        if hasattr(Building, "all_objects"):
            return Building.all_objects.all()
        return super().get_queryset(request)