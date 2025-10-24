import requests
from integrations.base.adapter import BaseAdapter


class JiraAdapter(BaseAdapter):
    def __init__(self, connection):
        self.access_token = connection.access_token
        self.cloud_id = connection.metadata.get("cloud_id")
        self.site_url = connection.metadata.get("site_url")
        self.base_url = f"https://api.atlassian.com/ex/jira/{self.cloud_id}/rest/api/3"

    def _headers(self):
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Accept": "application/json",
        }

    def get_project(self, project_id):
        url = f"{self.base_url}/project/{project_id}"
        resp = requests.get(url, headers=self._headers())
        resp.raise_for_status()
        return resp.json()

    def get_tasks(self, project_id):
        jql = f"project={project_id}"
        url = f"{self.base_url}/search/jql"
        resp = requests.get(url, headers=self._headers(), params={"jql": jql})
        resp.raise_for_status()
        issues = resp.json().get("issues", [])

        detailed_issues = []
        for issue in issues:
            url2 = f"{self.base_url}/issue/{issue['id']}"
            resp2 = requests.get(url2, headers=self._headers())
            resp2.raise_for_status()
            detailed_issues.append(resp2.json())
        return detailed_issues

    def transform_project(self, data):
        return {
            "id": data["id"],
            "title": data["name"],
            "provider": "jira",
        }

    def transform_task(self, issue):
        fields = issue["fields"]

        def extract_description(fields):
            desc = fields.get("description")
            try:
                return desc["content"][0]["content"][0]["text"]
            except (TypeError, KeyError, IndexError):
                return ""

        def extract_priority(fields):
            priority = fields.get("priority")
            try:
                return priority.get("name")
            except (TypeError, KeyError, IndexError):
                return ""

        return {
            "id": issue["id"],
            "title": fields.get("summary"),
            "description": extract_description(fields),
            "status": fields.get("status", {}).get("name"),
            "priority": extract_priority(fields),
            "external_url": f"{self.site_url}/browse/{issue['key']}",
            "custom_fields": fields,
        }
