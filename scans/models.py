import json

from django.db import models
from django.contrib.auth.models import User

from tasks.models import Configuration
from benchmarks.models import Benchmark, Control
from scans.transports import get_transport


class ScanControl(models.Model):
    STATUS_CHOICES = (
        (1, "Compliant"),
        (2, "Not compliant"),
        (3, "Not applicable"),
        (4, "Unknown"),
    )
    scan_benc = models.ForeignKey("ScanBenc", on_delete=models.CASCADE, related_name="scan_controls")
    control = models.ForeignKey(Control, on_delete=models.CASCADE)
    status = models.PositiveSmallIntegerField(choices=STATUS_CHOICES, default=4)
    result = models.TextField(blank=True, null=True)  # json

    class Meta:
        unique_together = (("scan_benc", "control"),)

    def __str__(self):
        return str(self.id)


class ScanBenc(models.Model):
    scan_host = models.ForeignKey("ScanHost", on_delete=models.CASCADE, related_name="scan_benchs")
    benchmark = models.ForeignKey(Benchmark, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.id)

    def unchecked_controls(self, status=4, message="<This control not checked>"):
        result = json.dumps([
            {
                "type": "message",
                "data": {
                    "head": "Error",
                    "text": message
                }
            }
        ])

        checked_controls_id = [control.control.id for control in self.scan_controls.all()]
        for control in self.benchmark.controls.all():
            if control.id not in checked_controls_id:
                ScanControl.objects.create(scan_benc=self, control=control, status=status,
                                           result=result)

    @property
    def calc_count_controls(self):
        safety_max, safety_now = 0, 0
        result = {1: 0, 2: 0, 3: 0, 4: 0}
        for control in self.scan_controls.all():
            if control.status != 3:
                safety_max += control.control.cost

                if control.status == 1:
                    safety_now += control.control.cost

            for status in result:
                if control.status == status:
                    result[status] += 1

        if safety_max == 0:
            safety = None
        else:
            safety = round(safety_now / safety_max * 100)

        return result[1], result[2], result[3], result[4], sum(result.values()), safety


class ScanHost(models.Model):
    scan = models.ForeignKey("Scan", on_delete=models.CASCADE, related_name="scan_hosts")
    host = models.CharField(max_length=64)
    error_message = models.CharField(max_length=64, blank=True, null=True)

    def __str__(self):
        return "{} {}".format(self.scan.name, self.host)

    @property
    def calc_count_controls(self):
        results = [0, 0, 0, 0]
        scan_benchs = self.scan_benchs
        for scan_bench in scan_benchs.all():
            results = list(map(lambda x: sum(x),
                               list(zip(results, scan_bench.calc_count_controls[:4]))))

        if sum(results) == 0:
            return results
        else:
            return [round(x / sum(results) * 100) for x in results]

    def get_transport(self, transport_name):
        conf_obj = self.scan.configuration
        return get_transport("registry", host=self.host, user=conf_obj.wmi_login,
                             passw=conf_obj.wmi_passw)

    def add_control(self, control_id, status, result):
        control = Control.objects.get(id=control_id)
        benchmark = control.benchmark

        scan_bench = self.scan_benchs.filter(benchmark=benchmark)

        if not scan_bench:
            scan_bench = ScanBenc.objects.create(scan_host=self, benchmark=benchmark)
        else:
            scan_bench = scan_bench.last()

        result_json = json.dumps(result)

        ScanControl.objects.create(scan_benc=scan_bench, control=control,status=status,
                                   result=result_json)

        print(f"Control [{control_id}]")


class Scan(models.Model):
    STATUS_CHOICES = (
        (1, "Waiting"),
        (2, "Ping hosts"),
        (3, "Check transport"),
        (4, "In progress"),
        (5, "Complete"),
        (6, "Failed")
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="scans")
    name = models.CharField(max_length=64, default="lol")
    configuration = models.ForeignKey(Configuration, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    finish_time = models.DateTimeField(blank=True, null=True)
    status = models.PositiveSmallIntegerField(choices=STATUS_CHOICES, default=1)

    @property
    def percent_worked(self):
        benchmarks = self.configuration.benchmarks.all()
        hosts = self.configuration.hosts

        controls_done = len(ScanControl.objects.filter(scan_benc__scan_host__scan=self))
        controls_all = len(Control.objects.filter(benchmark__in=benchmarks)) * len(hosts)

        return int(controls_done / controls_all * 100) if controls_all else 0

    def __str__(self):
        return "[{}] {}".format(self.id, self.name)


class Queue(models.Model):
    MAX_ACTIVE_SCANS = 4

    scan = models.ForeignKey(Scan, on_delete=models.CASCADE, related_name="scans")

    @staticmethod
    def check_queue(scan):
        if not Queue.objects.filter(scan=scan):
            Queue.objects.create(scan=scan)

        active_scans = Scan.objects.filter(status__in=(2, 3, 4))
        if len(active_scans) >= Queue.MAX_ACTIVE_SCANS:
            return False

        queue_scans = Queue.objects.all()
        if len(queue_scans) == 0 or queue_scans[0].scan == scan:
            Queue.objects.filter(scan=scan).delete()
            return True
        return False
