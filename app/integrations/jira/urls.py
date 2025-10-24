from django.urls import path

from . import views

urlpatterns = [
    path("login/", views.JiraLoginView.as_view()),
    path("auth/callback/", views.JiraCallbackView.as_view()),
    path("<str:project_id>/import/", views.JiraImportProjectView.as_view()),
]
