from django.contrib import admin

from .models import Project, ProviderConnection, Task


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "client",
        "connection",
        "sync_mode",
        "scope_locked",
        "baseline_task_count",
        "created_at",
    )
    list_filter = ("sync_mode", "scope_locked")
    search_fields = ("title", "external_project_id", "client__username")


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "status",
        "priority",
        "project",
        "external_id",
        "in_baseline",
        "scope_approved",
        "assigned_freelancer",
        "payment_status",
    )
    list_filter = ("status", "priority", "in_baseline", "scope_approved")
    search_fields = ("title", "external_id", "project__title")


@admin.register(ProviderConnection)
class ProviderConnectionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "provider",
        "masked_access_token",
        "created_at",
        "updated_at",
    )
    list_filter = ("provider",)
    search_fields = ("user__username", "provider")

    # Custom display method
    def masked_access_token(self, obj):
        if not obj.access_token:
            return "-"
        return f"{obj.access_token[:6]}...{obj.access_token[-4:]}"

    masked_access_token.short_description = "Access Token"
