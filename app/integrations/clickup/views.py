from urllib.parse import urlencode

import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core import signing
from django.shortcuts import redirect
from projects.import_pipeline import import_project
from projects.models import ProviderConnection
from rest_framework.exceptions import AuthenticationFailed, ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from integrations.factory import get_adapter

from .adapter import ClickUpAdapter

User = get_user_model()


class ClickUpLoginView(APIView):
    def get(self, request):
        if not request.user.is_authenticated:
            raise AuthenticationFailed("You must be logged in to connect ClickUp")

        state = signing.dumps({"user_id": request.user.id})

        params = {
            "client_id": settings.CLICKUP_CLIENT_ID,
            "redirect_uri": settings.REDIRECT_URI,
            "state": state,
        }
        url = f"{settings.CLICKUP_AUTH_URL}?{urlencode(params)}"
        return redirect(url)


class ClickUpCallbackView(APIView):
    def get(self, request):
        code = request.query_params.get("code")
        state = request.query_params.get("state")
        if not code or not state:
            raise ValidationError("Missing authorization code or state")

        # Verify signed state
        try:
            data = signing.loads(state, max_age=300)  # expires in 5 min
            user_id = data["user_id"]
        except signing.BadSignature:
            raise ValidationError("Invalid state parameter")
        except signing.SignatureExpired:
            raise ValidationError("State parameter has expired")

        resp = requests.post(
            settings.CLICKUP_TOKEN_URL,
            data={
                "client_id": settings.CLICKUP_CLIENT_ID,
                "client_secret": settings.CLICKUP_CLIENT_SECRET,
                "code": code,
            },
        )

        resp.raise_for_status()
        token_data = resp.json()
        access_token = token_data.get("access_token")

        if not access_token:
            raise ValidationError("No access token returned from ClickUp")

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise ValidationError("Invalid user")

        connection, created = ProviderConnection.objects.get_or_create(
            user=user,
            provider="clickup",
            defaults={"access_token": access_token},
        )

        if not created:
            connection.access_token = access_token
            connection.save(update_fields=["access_token"])

        return Response(
            {
                "message": "Successfully authenticated with ClickUp",
                "provider_connection_id": connection.id,
                "user_id": user.id,
            }
        )


def get_token(request, provider="clickup"):
    if request.user and request.user.is_authenticated:
        connection = ProviderConnection.objects.filter(
            user=request.user, provider=provider
        ).first()

        if connection and connection.access_token:
            return connection.access_token
        else:
            return Response(
                {"error": "No ClickUp connection found for this user"}, status=400
            )

    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        return auth_header.split(" ")[1]

    raise AuthenticationFailed("No access token found")


class ClickUpUserView(APIView):
    def get(self, request):
        access_token = get_token(request)
        resp = requests.get(
            "https://api.clickup.com/api/v2/user",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        resp.raise_for_status()
        return Response(resp.json())


class SpaceListsView(APIView):
    def get(self, request, space_id):
        access_token = get_token(request)
        adapter = ClickUpAdapter(access_token)
        return Response(adapter.get_space_lists(space_id))


class ImportClickUpProjectView(APIView):
    def post(self, request, list_id):
        access_token = get_token(request, provider="clickup")
        adapter = get_adapter("clickup", access_token)

        project_data = adapter.transform_project(adapter.get_project(list_id))
        task_data = [adapter.transform_task(t) for t in adapter.get_tasks(list_id)]

        if not project_data:
            return Response({"error": f"List {list_id} not found"}, status=404)

        connection = ProviderConnection.objects.filter(
            user=request.user, provider="clickup"
        ).first()

        # Import into DB
        project = import_project(
            user=request.user,
            provider="clickup",
            external_project_id=project_data["id"],
            project_data=project_data,
            task_data=task_data,
            connection=connection,
        )

        return Response(
            {
                "message": f"List {project_data['title']} imported",
                "project_id": project.id,
                "task_count": project.tasks.count(),
            }
        )
