from django.urls import path

from .views import (
    LoginView,
    LogoutView,
    MeProfileView,
    RefreshTokenView,
    WebLoginView,
    WebLogoutView,
    WebRegisterView,
)

app_name = "users"

urlpatterns = [
	path("auth/login/", LoginView.as_view(), name="login"),
	path("auth/refresh/", RefreshTokenView.as_view(), name="token_refresh"),
	path("auth/logout/", LogoutView.as_view(), name="logout"),
	path("me/profile/", MeProfileView.as_view(), name="me_profile"),
	path("web/login/", WebLoginView.as_view(), name="web_login"),
	path("web/register/", WebRegisterView.as_view(), name="web_register"),
	path("web/logout/", WebLogoutView.as_view(), name="web_logout"),
]
