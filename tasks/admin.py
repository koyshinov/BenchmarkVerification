from django.contrib import admin

from tasks.models import Configuration


@admin.register(Configuration)
class ConfigurationAdmin(admin.ModelAdmin):
    list_display = ("name", "benchmark_names", "hosts", "wmi_login", "deleted")
