from integrations.clickup.adapter import ClickUpAdapter


def get_adapter(input: str, token: str):
    """
    Get the adapter for a project management provider
    """
    provider = input.lower().strip()
    if provider.strip() == "clickup":
        return ClickUpAdapter(token)
    else:
        raise ValueError(f"Unsupported provider: {provider}")
