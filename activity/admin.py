from django.contrib import admin

from .models import ActivityRecord, PhysicalActivity


@admin.register(PhysicalActivity)
class PhysicalActivityAdmin(admin.ModelAdmin):
	list_display = ("name", "met_value", "intensity", "is_active")
	list_filter = ("intensity", "is_active")
	search_fields = ("name",)


@admin.register(ActivityRecord)
class ActivityRecordAdmin(admin.ModelAdmin):
	list_display = ("daily_record", "activity", "duration_min", "calories_burned_estimated")
	list_filter = ("activity",)
	search_fields = ("activity__name", "daily_record__user__username")
