from django.urls import path

from .views import (
    ActivityView,
    AddFoodView,
    DashboardView,
    HelpView,
    HistoryView,
    ProfileView,
)

app_name = "core"

urlpatterns = [
    path("", DashboardView.as_view(), name="home"),
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
    path("add-food/", AddFoodView.as_view(), name="add_food"),
    path("activity/", ActivityView.as_view(), name="activity"),
    path("history/", HistoryView.as_view(), name="history"),
    path("profile/", ProfileView.as_view(), name="profile"),
    path("ayuda/", HelpView.as_view(), name="help"),
]
