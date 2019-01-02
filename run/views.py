import threading
import importlib
import os
import re
import time
import pythoncom
import wmi
from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils import timezone

from scans.models import Scan, ScanHost, Queue, ScanBenc
from tasks.models import Configuration
from benchmarks.models import Benchmark


def ping_hosts(hosts):
    all_good = True
    result = []

    for host in hosts:
        response = os.system(f"ping {host} -n 1 -w 1")
        if response != 0:
            result.append([host, "Ping error"])
            all_good = False

    return all_good, result


def check_transport(hosts, conf):
    all_good = True
    result = []

    wmi_login = conf.wmi_login
    wmi_password = conf.wmi_passw

    pythoncom.CoInitialize()

    for host in hosts:
        try:
            wmi.WMI(computer=host, user=wmi_login, password=wmi_password)
        except Exception as e:
            result.append([host, "Transport connection error"])
            all_good = False
            print(str(e))

    return all_good, result


def run(request, name, conf):
    scripts_re = re.compile(r"^\d+_\w+\.py$")

    scan = Scan.objects.create(user=request.user, name=name, configuration=conf,
                               start_time=datetime.now(tz=timezone.utc))

    while not Queue.check_queue(scan):
        time.sleep(1)

    hosts = scan.configuration.hosts
    excluded_hosts = list()

    # Start scanning
    scan.status = 2  # Start ping hosts
    scan.save()
    ping_status, ping_result = ping_hosts(hosts)
    if not ping_status:
        for fail_host, message in ping_result:
            ScanHost.objects.create(scan=scan, host=fail_host, error_message=message)
            excluded_hosts.append(fail_host)

    scan.status = 3  # Start check transport
    scan.save()
    hosts = [host for host in hosts if host not in excluded_hosts]
    tran_status, tran_result = check_transport(hosts, conf)
    if not tran_status:
        for fail_host, message in tran_result:
            ScanHost.objects.create(scan=scan, host=fail_host, error_message=message)
            excluded_hosts.append(fail_host)

    scan.status = 4  # Start scan benchmarks
    scan.save()
    benchmarks = conf.benchmarks.all()

    hosts = [host for host in hosts if host not in excluded_hosts]

    if not hosts:
        scan.status = 6
        scan.finish_time = datetime.now(tz=timezone.utc)
        scan.save()

        return

    for host in hosts:
        scan_host = ScanHost.objects.create(scan=scan, host=host)
        for benchmark in benchmarks:
            print(benchmark.name)
            scan_bench = ScanBenc.objects.create(scan_host=scan_host, benchmark=benchmark)

            scripts_folder = benchmark.scripts_folder
            if not os.path.isdir(scripts_folder):
                print("Invalid scripts folder")
                return

            scripts = [file[:-3] for file in os.listdir(scripts_folder) if scripts_re.match(file)]

            scripts_corrupts = False

            for script in scripts:
                print(script)
                pack_path = "{}.{}".format(scripts_folder.replace("\\", "."), script)
                try:
                    script_pack = importlib.import_module(pack_path)
                    script_pack.main(scan_host)
                except Exception as e:
                    print(f"Exception in {pack_path}")
                    print(str(e))
                    scripts_corrupts = True

            message = "Scripts is corrupt!" if scripts_corrupts else "Control is not checked"
            scan_bench.unchecked_controls(message=message)

    scan.status = 5  # Finish scanning (Complete)
    scan.finish_time = datetime.now(tz=timezone.utc)
    scan.save()


@login_required(login_url="/login")
def run_page(request):
    data = {
        "benchmarks": tuple(
            (bench.name, bench.id) for bench in Benchmark.objects.all()
        ),
        "dirs": ("Run", ),
        "configurations": Configuration.objects.filter(deleted=False, user=request.user)
    }
    if request.method == "POST":
        name = request.POST.get("name")
        conf = request.POST.get("conf")

        if not name or not conf:
            data["messages"] = [
                {"type": "danger", "title": "Invalid format!", "text": "Some data is empty"}
            ]
            return render(request, 'run/run.html', data)

        config_obj = Configuration.objects.filter(id=conf, user=request.user)

        if not config_obj:
            data["messages"] = [
                {"type": "danger", "title": "Invalid format!", "text": "Configuration not found"}
            ]
            return render(request, 'run/run.html', data)

        conf = config_obj[0]

        thread = threading.Thread(target=run, args=(request, name, conf))
        thread.start()

        data["messages"] = [
            {"type": "success", "title": "Good!", "text": "Start scanning..."}
        ]

    return render(request, 'run/run.html', data)
