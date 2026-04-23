from rest_framework import status
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from core.permissions import IsProfileOwner
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
