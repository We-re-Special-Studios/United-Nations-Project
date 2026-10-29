from django.contrib import admin
from ..models import Item, ItemSection
from adminsortable2.admin import (SortableAdminMixin, SortableInlineAdminMixin)
import json
from django.http import JsonResponse
from django.shortcuts import render
from django.urls import path, reverse
from django.views.decorators.http import require_POST
from django.db import transaction
from django.utils.decorators import method_decorator

class ItemInline(SortableInlineAdminMixin, admin.TabularInline):
    model = Item
    extra = 0
    fields = ("name", "price_type", "ordering")
    show_change_link = True


@admin.register(ItemSection)
class ItemSectionAdmin(SortableAdminMixin, admin.ModelAdmin):
    change_list_template = "admin/un_app/itemsection/change_list.html"
    list_display = ("name", "table_number", "ordering")
    list_filter = ("table_number",)
    search_fields = ("name",)
    inlines = [ItemInline]
    
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context["ordering_url"] = reverse(
            "admin:un_app_itemsection_ordering"
        )
        return super().changelist_view(request, extra_context)

    def get_urls(self):
        urls = super().get_urls()

        custom_urls = [
            path(
                "balance-sheet-ordering/",
                self.admin_site.admin_view(self.ordering_view),
                name="un_app_itemsection_ordering",
            ),
            path(
                "balance-sheet-ordering/save/",
                self.admin_site.admin_view(self.save_ordering_view),
                name="un_app_itemsection_save_ordering",
            ),
        ]

        return custom_urls + urls

    def ordering_view(self, request):
        sections = (
            ItemSection.objects
            .prefetch_related("items")
            .order_by("table_number", "ordering", "id")
        )

        tables = {
            number: {
                "number": number,
                "sections": [],
            }
            for number in range(1, 6)
        }

        for section in sections:
            tables[section.table_number]["sections"].append(section)

        context = {
            **self.admin_site.each_context(request),
            "title": "Balance Sheet Ordering",
            "tables": tables.values(),
            "save_url": reverse(
                "admin:un_app_itemsection_save_ordering"
            ),
        }

        return render(
            request,
            "admin/un_app/balance_sheet_ordering.html",
            context,
        )

    @method_decorator(require_POST)
    def save_ordering_view(self, request):
        try:
            data = json.loads(request.body)
            changes = data["items"]

            if not isinstance(changes, list):
                raise ValueError("Items must be a list.")

            with transaction.atomic():
                seen_ids = set()

                for change in changes:
                    item_id = int(change["id"])
                    section_id = int(change["section_id"])
                    ordering = int(change["ordering"])

                    if (
                        item_id in seen_ids
                        or ordering < 0
                    ):
                        raise ValueError("Invalid item ordering.")

                    seen_ids.add(item_id)

                    item = Item.objects.get(pk=item_id)
                    section = ItemSection.objects.get(pk=section_id)

                    item.section = section
                    item.ordering = ordering
                    item.save(update_fields=["section", "ordering"])

            return JsonResponse({"success": True})

        except (
            ValueError,
            KeyError,
            TypeError,
            Item.DoesNotExist,
            ItemSection.DoesNotExist,
        ):
            return JsonResponse(
                {"success": False, "error": "Invalid ordering data."},
                status=400,
            )


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'price_type', 'market_value', "section", 'ordering')  
    search_fields = ('name', 'description', 'note', 'image_name')      
    list_filter = ("section__table_number", "section", "price_type")
    list_select_related = ("section",)
    ordering = ('ordering',)