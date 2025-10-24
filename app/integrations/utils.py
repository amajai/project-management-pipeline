from projects.models import ProviderConnection
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.response import Response


def get_token(request, provider):
    if request.user and request.user.is_authenticated:
        connection = ProviderConnection.objects.filter(
            user=request.user, provider=provider
        ).first()

        if connection and connection.access_token:
            return connection.access_token
        else:
            return Response({"error": "No connection found for this user"}, status=400)

    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        return auth_header.split(" ")[1]

    raise AuthenticationFailed("No access token found")
