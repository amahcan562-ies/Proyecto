from django.contrib.auth import login, logout
from django.shortcuts import redirect, render
from django.views import View
from rest_framework import status
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from core.permissions import IsProfileOwner
from .forms import UserLoginForm, UserRegisterForm
from .models import Profile
from .serializers import LogoutSerializer, ProfileSerializer


class LoginView(TokenObtainPairView):
	permission_classes = [AllowAny]


class RefreshTokenView(TokenRefreshView):
	permission_classes = [AllowAny]


class LogoutView(APIView):
	def post(self, request):
		serializer = LogoutSerializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		serializer.save()
		return Response(status=status.HTTP_205_RESET_CONTENT)


class MeProfileView(RetrieveUpdateAPIView):
	serializer_class = ProfileSerializer
	permission_classes = [IsAuthenticated, IsProfileOwner]

	def get_object(self):
		profile, _ = Profile.objects.get_or_create(user=self.request.user)
		self.check_object_permissions(self.request, profile)
		return profile


class WebLoginView(View):
	template_name = "users/login.html"

	def get(self, request):
		form = UserLoginForm(request)
		return render(request, self.template_name, {"form": form})

	def post(self, request):
		form = UserLoginForm(request, data=request.POST)
		if form.is_valid():
			login(request, form.get_user())
			return redirect("core:dashboard")
		return render(request, self.template_name, {"form": form})


class WebRegisterView(View):
	template_name = "users/register.html"

	def get(self, request):
		form = UserRegisterForm()
		return render(request, self.template_name, {"form": form})

	def post(self, request):
		form = UserRegisterForm(request.POST)
		if form.is_valid():
			user = form.save()
			login(request, user)
			return redirect("core:dashboard")
		return render(request, self.template_name, {"form": form})


class WebLogoutView(View):
	def post(self, request):
		logout(request)
		return redirect("users:web_login")
