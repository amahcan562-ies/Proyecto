from django.contrib import admin

from .models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
	list_display = ("user", "goal", "height_cm", "weight_kg", "target_weight_kg")
	search_fields = ("user__username", "user__email")
