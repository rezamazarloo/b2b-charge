from django.contrib import admin
from django.utils.html import format_html
from .models import CreditRequest, TransactionHistory
from django.utils.translation import gettext_lazy as _


# Register your models here.
@admin.register(CreditRequest)
class CreditRequestAdmin(admin.ModelAdmin):
    list_display = ("id", "amount", "user__email", "colored_status", "is_processed", "created_at")
    list_filter = ("status", "is_processed")
    search_fields = ("id", "user__first_name", "user__last_name", "user__email")
    ordering = ("-created_at",)
    readonly_fields = ("id", "created_at", "updated_at", "is_processed")
    autocomplete_fields = ("user",)
    date_hierarchy = "created_at"

    def colored_status(self, obj):
        colors = {
            "pending": "#ffa500",  # Orange
            "complete": "#28a745",  # Green
            "reject": "#dc3545",  # Red
        }
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            colors.get(obj.status, "#000000"),
            obj.get_status_display(),
        )

    colored_status.short_description = _("status")
    colored_status.admin_order_field = "status"


@admin.register(TransactionHistory)
class TransactionHistoryAdmin(admin.ModelAdmin):
    list_display = ("id", "colored_amount", "seller__email", "colored_type", "created_at")
    list_filter = ("type",)
    search_fields = ("id", "seller__first_name", "seller__last_name", "seller__email")
    ordering = ("-created_at",)
    readonly_fields = ("id", "created_at", "updated_at")
    autocomplete_fields = ("seller", "simcard", "credit_request")

    def colored_type(self, obj):
        colors = {
            "balance_top_up": "#007bff",  # Blue
            "simcard_charge": "#6f42c1",  # Green
        }
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            colors.get(obj.type, "#000000"),
            obj.get_type_display(),
        )

    colored_type.short_description = _("transaction type")
    colored_type.admin_order_field = "type"

    def colored_amount(self, obj):
        if obj.type == TransactionHistory.TypeChoices.BALANCE_TOP_UP:
            color = "#259543"
        elif obj.type == TransactionHistory.TypeChoices.SIMCARD_CHARGE:
            color = "#DD1111"
        else:
            color = "black"

        formatted_amount = f"{obj.amount:,.0f}"  # format with comma, no decimals
        return format_html('<strong style="color:{};">{}</strong>', color, formatted_amount)

    colored_amount.short_description = _("amount")
    colored_amount.admin_order_field = "amount"
