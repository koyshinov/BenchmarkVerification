import yaml

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import Http404

from benchmarks.models import Benchmark, Control


@login_required(login_url="/login")
def benchmark_view(request, benchmark_id):
    benchmark_obj = Benchmark.objects.filter(id=benchmark_id)

    if not benchmark_obj:
        raise Http404("Benchmark not found")

    benchmark = benchmark_obj[0]

    control_obj = Control.objects.filter(benchmark=benchmark)

    controls = list()

    for obj in control_obj:
        data = yaml.load(obj.information)
        controls.append(
            {
                "id": "{:0>4}".format(obj.id),
                "title": data.get("Title", ""),
                "description": data.get("Description", ""),
                "rationale": data.get("Rationale", ""),
                "audit": data.get("Audit", ""),
                "remediation": data.get("Remediation", ""),
                "impact": data.get("Impact", "")
            }
        )

    data = {
        "benchmarks": tuple(
            (bench.name, bench.id) for bench in Benchmark.objects.all()
        ),
        "benchmark_name": benchmark.name,
        "controls": controls,
        "dirs": ("Benchmarks", benchmark.name)
    }

    return render(request, 'benchmark_page.html', data)