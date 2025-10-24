from django.urls import path

from . import views

urlpatterns = [
    path("login/", views.ClickUpLoginView.as_view()),
    path("auth/callback/", views.ClickUpCallbackView.as_view()),
    path("<str:list_id>/import/", views.ClickUpImportProjectView.as_view()),
]
