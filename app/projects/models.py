from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Project(models.Model):
    PROVIDERS = [
        ("clickup", "ClickUp"),
        ("jira", "Jira"),
        ("asana", "Asana"),
        ("trello", "Trello"),
        ("monday", "Monday"),
    ]

    SYNC_MODES = [
        ("import_once", "Import Once"),
        ("read_only", "Read Only"),
        ("controlled", "Controlled Sync"),
    ]

    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name="projects")
    provider = models.CharField(max_length=20, choices=PROVIDERS)
    external_project_id = models.CharField(max_length=255)
    title = models.CharField(max_length=255)
    sync_mode = models.CharField(
        max_length=20, choices=SYNC_MODES, default="import_once"
    )
    scope_locked = models.BooleanField(default=False)

    baseline_task_ids = models.JSONField(default=list)
    baseline_task_count = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)


class Task(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="tasks")
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=50)
    priority = models.CharField(max_length=50, null=True, blank=True)

    provider = models.CharField(max_length=20)
    external_id = models.CharField(max_length=255)
    external_url = models.URLField(blank=True, null=True)

    in_baseline = models.BooleanField(default=False)
    scope_approved = models.BooleanField(default=True)

    assigned_freelancer = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_tasks",
    )
    hourly_rate = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    time_tracked = models.FloatField(default=0)
    payment_status = models.CharField(max_length=20, default="unpaid")

    custom_fields = models.JSONField(default=dict)
