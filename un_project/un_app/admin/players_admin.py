from django.contrib import admin
from ..models import Player

@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = (
        'username',
        'nation',
        'un_rep',
        'num_buildings_built_display',  # custom column
    )
    search_fields = (
        'username',
        'nation__name',  # allows searching by nation name
        'nation__abbreviation',
        'description',
    )
    list_filter = ('un_rep', 'nation',)
    ordering = ('username',)

    @admin.display(description="Buildings Built")
    def num_buildings_built_display(self, obj):
        return obj.num_buildings_built()