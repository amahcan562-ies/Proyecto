from django.contrib import admin

from .models import DailyEvaluation, DailyRecord


@admin.register(DailyRecord)
class DailyRecordAdmin(admin.ModelAdmin):
	list_display = ("user", "date", "water_intake_ml", "updated_at")
	list_filter = ("date",)
	search_fields = ("user__username", "user__email")


@admin.register(DailyEvaluation)
class DailyEvaluationAdmin(admin.ModelAdmin):
	list_display = ("daily_record", "score", "updated_at")
	list_filter = ("score",)
	search_fields = ("daily_record__user__username",)
