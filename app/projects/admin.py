from django.contrib import admin

from .models import Project, Task


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "provider",
        "client",
        "sync_mode",
        "scope_locked",
        "baseline_task_count",
        "created_at",
    )
    list_filter = ("provider", "sync_mode", "scope_locked", "created_at")
    search_fields = (
        "title",
        "external_project_id",
        "client__username",
        "client__email",
    )
    readonly_fields = ("baseline_task_ids", "baseline_task_count", "created_at")

    fieldsets = (
        (
            "Project Info",
            {"fields": ("title", "client", "provider", "external_project_id")},
        ),
        ("Sync Settings", {"fields": ("sync_mode", "scope_locked")}),
    )


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "status",
        "priority",
        "project",
        "provider",
        "in_baseline",
        "scope_approved",
        "assigned_freelancer",
        "payment_status",
    )
    list_filter = (
        "status",
        "priority",
        "provider",
        "in_baseline",
        "scope_approved",
        "payment_status",
    )
    search_fields = (
        "title",
        "description",
        "external_id",
        "external_url",
        "assigned_freelancer__username",
        "assigned_freelancer__email",
    )
    autocomplete_fields = ("project", "assigned_freelancer")
    readonly_fields = ("external_id", "external_url", "custom_fields")
