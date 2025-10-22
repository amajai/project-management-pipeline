from django.contrib.auth import get_user_model

from .models import Project, Task

User = get_user_model()


def import_clickup_project(
    user, provider, external_project_id, project_data, task_data
):
    if user.is_anonymous:  # fallback
        user = User.objects.first()

    # Create Project
    project, created = Project.objects.get_or_create(
        client=user,
        provider=provider,
        external_project_id=external_project_id,
        defaults={
            "title": project_data["name"],
            "baseline_task_ids": [t["id"] for t in task_data],
            "baseline_task_count": len(task_data),
        },
    )

    # Create Tasks
    for t in task_data:
        Task.objects.get_or_create(
            project=project,
            external_id=t["id"],
            defaults={
                "title": t["name"],
                "description": t.get("text_content", ""),
                "status": t.get("status", {}).get("status", "Undefined"),
                "priority": t.get("priority", None),
                "external_url": t.get("url"),
                "in_baseline": True,
                "scope_approved": True,
                "custom_fields": t.get("custom_fields", []),
            },
        )

    return project
