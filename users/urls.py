from django.urls import path

from .views import LoginView, LogoutView, MeProfileView, RefreshTokenView

app_name = "users"

urlpatterns = [
	path("auth/login/", LoginView.as_view(), name="login"),
	path("auth/refresh/", RefreshTokenView.as_view(), name="token_refresh"),
	path("auth/logout/", LogoutView.as_view(), name="logout"),
	path("me/profile/", MeProfileView.as_view(), name="me_profile"),
]

