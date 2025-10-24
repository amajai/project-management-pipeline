import requests
from django.conf import settings

from integrations.base.adapter import BaseAdapter


class ClickUpAdapter(BaseAdapter):
    BASE_URL = settings.CLICKUP_BASE_URL

    def __init__(self, connection):
        self.access_token = connection.access_token

    def _headers(self):
        return {"Authorization": f"Bearer {self.access_token}"}

    def get_project(self, list_id: str):
        """Get list metadata (acts as 'project' in ClickUp)."""
        resp = requests.get(f"{self.BASE_URL}/list/{list_id}", headers=self._headers())
        resp.raise_for_status()
        return resp.json()

    def get_tasks(self, list_id: str):
        """Get all tasks inside a list."""
        resp = requests.get(
            f"{self.BASE_URL}/list/{list_id}/task", headers=self._headers()
        )
        resp.raise_for_status()
        return resp.json().get("tasks", [])

    def transform_project(self, raw_data: dict) -> dict:
        return {
            "id": raw_data["id"],
            "title": raw_data["name"],
            "provider": "clickup",
        }

    def transform_task(self, raw_data: dict) -> dict:
        return {
            "id": raw_data["id"],
            "title": raw_data["name"],
            "description": raw_data.get("text_content", ""),
            "status": raw_data.get("status", {}).get("status", "todo"),
            "priority": raw_data.get("priority", None),
            "external_url": raw_data.get("url"),
            "custom_fields": raw_data.get("custom_fields", []),
        }

    def get_space_lists(self, space_id: str):
        resp = requests.get(
            f"{self.BASE_URL}/space/{space_id}/list",
            headers=self._headers(),
        )
        resp.raise_for_status()
        return resp.json().get("lists", [])
