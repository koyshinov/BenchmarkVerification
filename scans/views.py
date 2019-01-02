import yaml
import json

from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import render

from benchmarks.models import Benchmark, Control
from scans.models import Scan, ScanHost, ScanBenc, ScanControl


@login_required(login_url="/login")
def scan_tables(request):
    in_progress_scans = Scan.objects.filter(user=request.user, status__in=(1, 2, 3, 4))\
                                    .order_by("-id")
    scan_results = Scan.objects.filter(user=request.user, status__in=(5, 6)).order_by("-id")

    data = {
        "benchmarks": tuple(
            (bench.name, bench.id) for bench in Benchmark.objects.all()
        ),
        "dirs": ("Results",),

        "in_process": in_progress_scans,
        "scan_results": scan_results
    }
    return render(request, 'scans/scan_results.html', data)


@login_required(login_url="/login")
def scan_host_result(request, scan_id, hostname):
    scan_benchs = ScanBenc.objects.filter(scan_host__scan__user=request.user,
                                          scan_host__scan__id=scan_id, scan_host__host=hostname)

    if not scan_benchs:
        raise Http404("Host scan not found")

    scan = Scan.objects.get(id=scan_id)

    start_time = scan.start_time.strftime('%d.%m.%Y %H:%M:%S') if scan.start_time else "None"
    finish_time = scan.finish_time.strftime('%d.%m.%Y %H:%M:%S') if scan.finish_time else "None"

    data = {
        "benchmarks": tuple(
            (bench.name, bench.id) for bench in Benchmark.objects.all()
        ),
        "dirs": ("Results", scan.name, hostname),

        "scan_id": scan_id,
        "host": hostname,

        "host_info": [
            ["Scan Name", scan.name],
            ["Hostname", hostname],
            ["Username", scan.configuration.wmi_login],
            ["Start Time", start_time],
            ["Finish Time", finish_time],
        ],
        "benchmark_results": scan_benchs
    }
    return render(request, 'scans/host_results.html', data)


@login_required(login_url="/login")
def scan_bench_result(request, scan_id, hostname, benchmark_id):
    scan_controls = ScanControl.objects.filter(
        scan_benc__scan_host__scan__user=request.user,
        scan_benc__scan_host__scan__id=scan_id,
        scan_benc__scan_host__host=hostname,
        scan_benc__benchmark__id=benchmark_id
    ).order_by("control__id")

    if not scan_controls:
        raise Http404("Bench scan not found")

    benchmark = Benchmark.objects.get(id=benchmark_id)
    scan = Scan.objects.get(id=scan_id)
    controls = list()

    for obj in scan_controls:
        # TODO: Отловить ошибки парсинга json
        try:
            result = json.loads(obj.result) if obj.result else ""
        except json.JSONDecodeError:
            result = [{"type":"message", "data":{"head":"Error", "text":"<Parsing Error>"}}]
        data = yaml.load(obj.control.information)
        controls.append(
            {
                "id": obj.control.id,
                "title": data.get("Title", ""),
                "description": data.get("Description", ""),
                "rationale": data.get("Rationale", ""),
                "result": result,
                "remediation": data.get("Remediation", ""),
                "impact": data.get("Impact", ""),
                "status": obj.status
            }
        )

    data = {
        "benchmarks": tuple(
            (bench.name, bench.id) for bench in Benchmark.objects.all()
        ),
        "benchmark_name": benchmark.name,
        "controls": controls,
        "dirs": ("Results", scan.name, hostname, benchmark.name)
    }

    return render(request, 'scans/benc_results.html', data)
