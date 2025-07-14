from django.contrib import admin
from .models import SimCard


@admin.register(SimCard)
class SimCardAdmin(admin.ModelAdmin):
    list_display = ["number", "operator", "balance"]
    list_filter = ["operator"]
    search_fields = ["number"]
    readonly_fields = ["id", "created_at", "updated_at"]
    date_hierarchy = "created_at"
