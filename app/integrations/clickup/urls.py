from django.urls import path

from . import views

urlpatterns = [
    path("login/", views.ClickUpLoginView.as_view()),
    path("auth/callback/", views.ClickUpCallbackView.as_view()),
    path("teams/", views.ClickUpTeamsView.as_view()),
    path("user/", views.ClickUpUserView.as_view()),
    path("<str:space_id>/lists/", views.SpaceListsView.as_view()),
    path("<str:list_id>/tasks/", views.ListTasksView.as_view()),
    path("<str:space_id>/projects/", views.SpaceProjectsView.as_view()),
]
