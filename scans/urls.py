from django.conf.urls import url

from scans.views import scan_tables, scan_host_result, scan_bench_result


urlpatterns = [
    url(r'results$', scan_tables),
    url(r'scan_(?P<scan_id>\d+)/host_(?P<hostname>[\w\.\-]+)$', scan_host_result),
    url(r'scan_(?P<scan_id>\d+)/host_(?P<hostname>[\w\.\-]+)/bench_(?P<benchmark_id>\d+)$',
        scan_bench_result),
]
