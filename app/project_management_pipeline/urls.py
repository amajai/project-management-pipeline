import psycopg
from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from rest_framework.response import Response
from rest_framework.views import APIView


class DBCheckView(APIView):
    def get(self, request):
        try:
            conn = psycopg.connect(
                dbname=settings.DATABASES["default"]["NAME"],
                user=settings.DATABASES["default"]["USER"],
                password=settings.DATABASES["default"]["PASSWORD"],
                host=settings.DATABASES["default"]["HOST"],
            )
            cur = conn.cursor()
            cur.execute("SELECT version();")
            version = cur.fetchone()
            conn.close()
            return Response({"database_version": version})
        except Exception as e:
            return Response({"error": str(e)})


class HealthCheckView(APIView):
    def get(self, request):
        return Response(
            {"message": "Django REST Framework with PostgreSQL is running!"}
        )


urlpatterns = [
    path("admin/", admin.site.urls),
    path("db-check/", DBCheckView.as_view()),
    path("health/", HealthCheckView.as_view()),
    path("clickup/", include("integrations.clickup.urls")),
]
