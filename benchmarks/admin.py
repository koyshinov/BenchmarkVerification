from django.contrib import admin

from benchmarks.models import Benchmark, Control


@admin.register(Benchmark)
class BenchmarkAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "work_status", "comment")


@admin.register(Control)
class ControlAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "benchmark", "work_status", "comment")
