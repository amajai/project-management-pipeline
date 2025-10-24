from projects.models import ProviderConnection

from integrations.clickup.adapter import ClickUpAdapter
from integrations.jira.adapter import JiraAdapter


def get_adapter(input: str, connection: ProviderConnection):
    """
    Get the adapter for a project management provider
    """
    provider = input.lower().strip()
    if provider.strip() == "clickup":
        return ClickUpAdapter(connection)
    if provider == "jira":
        return JiraAdapter(connection)
    else:
        raise ValueError(f"Unsupported provider: {provider}")
