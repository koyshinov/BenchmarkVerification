import re

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods

from tasks.models import Configuration
from benchmarks.models import Benchmark


@login_required(login_url="/login")
@require_http_methods(["GET"])
def configuration_view(request):
    configuration_objs = Configuration.objects.filter(deleted=False, user=request.user)
    configurations = (
        (
            conf_obj.id,
            conf_obj.name,
            conf_obj.benchmark_names,
            conf_obj.hosts,
            conf_obj.wmi_login
        ) for conf_obj in configuration_objs
    )

    data = {
        "benchmarks": tuple(
            (bench.name, bench.id) for bench in Benchmark.objects.all()
        ),
        "configurations": configurations,
        "dirs": ("Configurations", "Table")
    }

    return render(request, 'task/table.html', data)


@login_required(login_url="/login")
def create_task(request):
    data = {
        "benchmarks": tuple(
            (bench.name, bench.id) for bench in Benchmark.objects.all()
        ),
        "dirs": ("Configurations", "Create")
    }

    if request.method != "POST":
        return render(request, 'task/create.html', data)

    name = request.POST.get("name")
    benchmarks = dict(request.POST).get("benchmarks")
    hosts = request.POST.get("hosts")
    wmi_login = request.POST.get("wmi_login")
    wmi_passw = request.POST.get("wmi_passw")
    wmi_passw2 = request.POST.get("wmi_passw2")

    if not all([name, hosts, wmi_login, wmi_passw, wmi_passw2]):
        data["messages"] = [
            {"type": "danger", "title": "Invalid configuration!", "text": "Some data is empty"}
        ]
        return render(request, 'task/create.html', data)

    if not benchmarks:
        data["messages"] = [
            {"type": "danger", "title": "Invalid configuration!", "text": "Choose benchmarks"}
        ]
        return render(request, 'task/create.html', data)

    if wmi_passw != wmi_passw2:
        data["messages"] = [
            {"type": "danger", "title": "Invalid configuration!", "text": "Passwords do not match"}
        ]
        return render(request, 'task/create.html', data)

    corrupt_hosts = True
    hosts_items = re.split(r"[\s;,]+", hosts)
    for host in hosts_items:
        numbers = host.split(".")
        if len(numbers) != 4:
            break
        if not all(map(lambda n: n.isdigit(), numbers)):
            break
        if not all(int(n) in range(0, 256) for n in numbers):
            break
    else:
        corrupt_hosts = False

    if corrupt_hosts:
        data["messages"] = [
            {"type": "danger", "title": "Invalid configuration!",
             "text": "Hosts format is not correct"}
        ]
        return render(request, 'task/create.html', data)

    try:
        benchs = [Benchmark.objects.get(id=bench) for bench in benchmarks]
    except Benchmark.DoesNotExist:
        data["messages"] = [
            {"type": "danger", "title": "Invalid configuration!",
             "text": "Some benchmarks not found"}
        ]
        return render(request, 'task/create.html', data)


    configuration = Configuration.objects.create(user=request.user, name=name, hosts_text=hosts,
                                                 wmi_login=wmi_login, wmi_passw=wmi_passw)

    configuration.benchmarks.add(*benchs)

    return redirect("/task/table")


@login_required(login_url="/login")
def delete_task(request, task_id):
    Configuration.objects.filter(user=request.user, id=task_id).update(deleted=True)
    return redirect("/task/table")
