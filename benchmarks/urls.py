from django.conf.urls import url

from benchmarks.views import benchmark_view


urlpatterns = [
    url(r'about/(?P<benchmark_id>\d+)$', benchmark_view),
]
