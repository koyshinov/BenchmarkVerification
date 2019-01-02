import re

from django.db import models
from django.contrib.auth.models import User

from benchmarks.models import Benchmark


class Configuration(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="configurations")
    name = models.CharField(max_length=64)
    benchmarks = models.ManyToManyField(Benchmark, related_name="configurations")
    hosts_text = models.TextField()
    wmi_login = models.CharField(max_length=64)
    wmi_passw = models.CharField(max_length=64)
    deleted = models.BooleanField(default=False)

    @property
    def benchmark_names(self):
        return [bench.name for bench in self.benchmarks.all()]

    @property
    def hosts(self):
        hosts = re.split(r"[\s;,]+", str(self.hosts_text)) if self.hosts_text else []
        return hosts

    def __str__(self):
        return self.name
