from django.conf.urls import url

from tasks.views import configuration_view, create_task, delete_task

urlpatterns = [
    url(r'table$', configuration_view),
    url(r'create$', create_task),
    url(r'^delete/(?P<task_id>\d+)$', delete_task),
]
