from urllib.parse import urlencode

import requests
from django.conf import settings
from django.shortcuts import redirect
from projects.import_pipeline import import_project
from rest_framework.exceptions import AuthenticationFailed, ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from integrations.factory import get_adapter

from .adapter import ClickUpAdapter


class ClickUpLoginView(APIView):
    def get(self, request):
        params = {
            "client_id": settings.CLICKUP_CLIENT_ID,
            "redirect_uri": settings.REDIRECT_URI,
        }
        url = f"{settings.CLICKUP_AUTH_URL}?{urlencode(params)}"
        return redirect(url)


class ClickUpCallbackView(APIView):
    def get(self, request):
        code = request.query_params.get("code")
        if not code:
            raise ValidationError("No authorization code provided")

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

        return Response(
            {
                "message": "Successfully authenticated with ClickUp",
                "token_info": token_data,
            }
        )


def get_token(request):
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise AuthenticationFailed("Missing Authorization header")
    if auth_header.startswith("Bearer "):
        return auth_header.split(" ")[1]
    return auth_header


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
        access_token = get_token(request)

        adapter = get_adapter("clickup", access_token)

        project_data = adapter.transform_project(adapter.get_project(list_id))
        task_data = [adapter.transform_task(t) for t in adapter.get_tasks(list_id)]

        if not project_data:
            return Response({"error": f"List {list_id} not found"}, status=404)

        print(project_data)
        # Import into DB
        project = import_project(
            user=request.user,
            provider="clickup",
            external_project_id=project_data["id"],
            project_data=project_data,
            task_data=task_data,
        )

        return Response(
            {
                "message": f"List {project_data['title']} imported",
                "project_id": project.id,
                "task_count": project.tasks.count(),
            }
        )
