from django.contrib import admin

from .models import Food, FoodConsumption


@admin.register(Food)
class FoodAdmin(admin.ModelAdmin):
	list_display = ("name", "brand", "calories_per_100g", "is_active")
	list_filter = ("is_active",)
	search_fields = ("name", "brand")


@admin.register(FoodConsumption)
class FoodConsumptionAdmin(admin.ModelAdmin):
	list_display = ("daily_record", "food", "amount_g", "meal_type", "consumed_at")
	list_filter = ("meal_type",)
	search_fields = ("food__name", "daily_record__user__username")
