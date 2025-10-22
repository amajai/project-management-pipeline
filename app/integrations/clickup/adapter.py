import requests
from django.conf import settings


class ClickUpAdapter:
    BASE_URL = settings.CLICKUP_BASE_URL

    def __init__(self, access_token: str):
        self.access_token = access_token
        self.headers = {"Authorization": f"Bearer {self.access_token}"}

    def get_list(self, list_id):
        resp = requests.get(
            f"{self.BASE_URL}/list/{list_id}",
            headers={"Authorization": f"Bearer {self.access_token}"},
        )
        resp.raise_for_status()
        return resp.json()

    def fetch_space_lists(self, space_id: str):
        resp = requests.get(
            f"{self.BASE_URL}/space/{space_id}/list", headers=self.headers
        )
        resp.raise_for_status()
        return resp.json().get("lists", [])

    def fetch_list_tasks(self, list_id: str, include_closed: bool = True):
        resp = requests.get(
            f"{self.BASE_URL}/list/{list_id}/task",
            headers=self.headers,
            params={"include_closed": str(include_closed).lower(), "subtasks": "true"},
        )
        resp.raise_for_status()
        data = resp.json().get("tasks", [])

        # Nest subtasks
        task_map = {t["id"]: {**t, "subtasks": []} for t in data}
        for task in data:
            parent_id = task.get("parent")
            if parent_id and parent_id in task_map:
                task_map[parent_id]["subtasks"].append(task_map[task["id"]])

        def clean_task(t):
            return {**t, "subtasks": [clean_task(st) for st in t["subtasks"]]}

        return [clean_task(t) for t in task_map.values() if not t.get("parent")]

    def get_space_lists(self, space_id: str):
        return self.fetch_space_lists(space_id)

    def get_list_tasks(self, list_id: str, include_closed: bool = True):
        return self.fetch_list_tasks(list_id, include_closed)

    def get_space_projects(self, space_id: str, include_closed: bool = True):
        lists = self.fetch_space_lists(space_id)
        projects = []
        for lst in lists:
            tasks = self.fetch_list_tasks(lst["id"], include_closed)
            projects.append({**lst, "tasks": tasks})
        return projects
