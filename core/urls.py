from django.urls import path

from .views import HelpView, HomeView

app_name = "core"

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("ayuda/", HelpView.as_view(), name="help"),
]

