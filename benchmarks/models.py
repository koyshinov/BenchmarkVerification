from django.db import models


WORK_STATUSES = (
    (1, "active"),
    (2, "debug"),
    (3, "in progress"),
    (4, "non active")
)


class Benchmark(models.Model):
    name = models.CharField(max_length=64)
    work_status = models.PositiveSmallIntegerField(choices=WORK_STATUSES, blank=True, null=True)
    original_doc = models.FileField(blank=True, null=True)
    comment = models.CharField(max_length=64, blank=True, null=True)
    scripts_folder = models.CharField(max_length=512)

    class Meta:
        unique_together = (("name",),)

    def __str__(self):
        return self.name


class Control(models.Model):
    id = models.PositiveIntegerField(primary_key=True)
    name = models.CharField(max_length=64)
    benchmark = models.ForeignKey(Benchmark, on_delete=models.CASCADE, related_name="controls")
    information = models.TextField(blank=True, null=True)  # yaml
    work_status = models.PositiveSmallIntegerField(choices=WORK_STATUSES, blank=True, null=True)
    cost = models.PositiveSmallIntegerField()
    comment = models.CharField(max_length=64, blank=True, null=True)

    def __str__(self):
        return "[{:0>4}] {}".format(self.id, self.name)
