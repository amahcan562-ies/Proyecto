from django.conf import settings
from django.contrib import admin
from django.contrib.admin import AdminSite
from django.http import HttpResponseNotFound

from activity.models import PhysicalActivity
from nutrition.models import Food


class NutriTrackAdminSite(AdminSite):
    site_header = "NutriTrack Admin"
    site_title = "NutriTrack Admin"
    index_title = "Administracion"

    def _host_allowed(self, request):
        allowed_hosts = getattr(settings, "ADMIN_ALLOWED_HOSTS", [])
        if not allowed_hosts:
            return False
        host = request.get_host().split(":")[0]
        return host in allowed_hosts

    def _user_allowed(self, user):
        if not user.is_authenticated or not user.is_active or not user.is_superuser:
            return False
        admin_username = getattr(settings, "ADMIN_USERNAME", "")
        if admin_username:
            return user.get_username() == admin_username
        return True

    def has_permission(self, request):
        if not self._host_allowed(request):
            return False
        return self._user_allowed(request.user)

    def login(self, request, extra_context=None):
        if not self._host_allowed(request):
            return HttpResponseNotFound("Not Found")
        return super().login(request, extra_context=extra_context)


class FoodAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "brand",
        "calories_per_100g",
        "protein_per_100g",
        "carbs_per_100g",
        "fat_per_100g",
        "fiber_per_100g",
        "is_active",
    )
    list_filter = ("is_active",)
    search_fields = ("name", "brand")
    fields = (
        "name",
        "brand",
        "image_url",
        "calories_per_100g",
        "protein_per_100g",
        "carbs_per_100g",
        "fat_per_100g",
        "fiber_per_100g",
        "is_active",
    )


class PhysicalActivityAdmin(admin.ModelAdmin):
    list_display = ("name", "met_value", "intensity", "is_active")
    list_filter = ("intensity", "is_active")
    search_fields = ("name",)
    fields = (
        "name",
        "met_value",
        "intensity",
        "is_active",
    )

admin_site = NutriTrackAdminSite(name="nutritrack_admin")
admin_site.register(Food, FoodAdmin)
admin_site.register(PhysicalActivity, PhysicalActivityAdmin)
