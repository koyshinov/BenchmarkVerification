from django.contrib import admin

from scans.models import Scan, ScanHost, ScanBenc, ScanControl, Queue


@admin.register(Scan)
class ScanAdmin(admin.ModelAdmin):
    pass


# @admin.register(ScanHost)
# class ScanHostAdmin(admin.ModelAdmin):
#     pass
#
#
# @admin.register(ScanBenc)
# class ScanBencAdmin(admin.ModelAdmin):
#     pass
#
#
# @admin.register(ScanControl)
# class ScanControlAdmin(admin.ModelAdmin):
#     list_display = ("id", "scan_benc", "control", "status")


@admin.register(Queue)
class QueueAdmin(admin.ModelAdmin):
    pass
