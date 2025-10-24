from urllib.parse import urlencode

import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core import signing
from django.shortcuts import redirect
from integrations.factory import get_adapter
from projects.import_pipeline import import_project
from projects.models import ProviderConnection
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

User = get_user_model()


class JiraLoginView(APIView):
    def get(self, request):
        if not request.user.is_authenticated:
            raise ValidationError("Login required")

        state = signing.dumps({"user_id": request.user.id})
        params = {
            "audience": "api.atlassian.com",
            "client_id": settings.JIRA_CLIENT_ID,
            "scope": "offline_access read:jira-user read:jira-work",
            "redirect_uri": settings.JIRA_REDIRECT_URI,
            "state": state,
            "response_type": "code",
            "prompt": "consent",
        }
        url = f"{settings.JIRA_AUTH_URL}?{urlencode(params)}"
        return redirect(url)


class JiraCallbackView(APIView):
    def get(self, request):
        code = request.query_params.get("code")
        state = request.query_params.get("state")
        if not code or not state:
            raise ValidationError("Missing code or state")

        try:
            data = signing.loads(state, max_age=300)
            user = User.objects.get(id=data["user_id"])
        except Exception:
            raise ValidationError("Invalid state")

        resp = requests.post(
            settings.JIRA_TOKEN_URL,
            json={
                "grant_type": "authorization_code",
                "client_id": settings.JIRA_CLIENT_ID,
                "client_secret": settings.JIRA_CLIENT_SECRET,
                "code": code,
                "redirect_uri": settings.JIRA_REDIRECT_URI,
            },
            headers={"Content-Type": "application/json"},
        )
        resp.raise_for_status()
        token_data = resp.json()

        access_token = token_data.get("access_token")
        refresh_token = token_data.get("refresh_token")

        print(token_data)
        if not access_token:
            raise ValidationError("No access token from Jira")

        # Get cloudId
        r2 = requests.get(
            "https://api.atlassian.com/oauth/token/accessible-resources",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        r2.raise_for_status()
        resources = r2.json()
        if not resources:
            raise ValidationError("No Jira resources accessible for this user")

        site = resources[0]
        cloud_id = site["id"]
        site_url = site["url"]

        connection, created = ProviderConnection.objects.get_or_create(
            user=user,
            provider="jira",
            defaults={
                "access_token": access_token,
                "refresh_token": refresh_token,
                "metadata": {"cloud_id": cloud_id, "site_url": site_url},
            },
        )

        if not created:
            connection.access_token = access_token
            connection.refresh_token = refresh_token
            connection.metadata = {"cloud_id": cloud_id, "site_url": site_url}
            connection.save()

        return Response(
            {
                "message": "Connected to Jira",
                "connection_id": connection.id,
                "cloud_id": cloud_id,
                "site_url": site_url,
            }
        )


class JiraImportProjectView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, project_id):
        connection = ProviderConnection.objects.filter(
            user=request.user, provider="jira"
        ).first()
        if not connection:
            return Response({"error": "No Jira connection"}, status=400)
        adapter = get_adapter("jira", connection)

        project_data = adapter.transform_project(adapter.get_project(project_id))
        tasks = [adapter.transform_task(t) for t in adapter.get_tasks(project_id)]

        project = import_project(
            user=request.user,
            external_project_id=project_data["id"],
            project_data=project_data,
            task_data=tasks,
            connection=connection,
        )

        return Response(
            {
                "message": f"Imported Jira project {project_data['title']}",
                "project_id": project.id,
                "task_count": project.tasks.count(),
            }
        )
