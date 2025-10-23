from django.contrib.auth import get_user_model

from projects.models import Project, Task

User = get_user_model()


def import_project(
    user, provider, external_project_id, project_data, task_data, connection=None
):
    if user.is_anonymous:  # TODO: Assign users to project
        user = User.objects.first()

    project, created = Project.objects.get_or_create(
        client=user,
        external_project_id=external_project_id,
        defaults={
            "title": project_data["title"],
            "baseline_task_ids": [t["id"] for t in task_data],
            "baseline_task_count": len(task_data),
            "connection": connection,
        },
    )

    for t in task_data:
        Task.objects.get_or_create(
            project=project,
            external_id=t["id"],
            defaults={
                "title": t["title"],
                "description": t.get("description", ""),
                "status": t.get("status", "todo"),
                "priority": t.get("priority"),
                "external_url": t.get("external_url"),
                "in_baseline": True,
                "scope_approved": True,
                "custom_fields": t.get("custom_fields", {}),
            },
        )

    return project
