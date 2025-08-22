from django.db import models

class Machine(models.Model):
    hostname = models.CharField(max_length=255, unique=True)
    api_key = models.CharField(max_length=255)
    last_seen = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.hostname

class Snapshot(models.Model):
    machine = models.ForeignKey(Machine, on_delete=models.CASCADE, related_name='snapshots')
    collected_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [models.Index(fields=['machine', '-collected_at'])]

    def __str__(self):
        return f"{self.machine.hostname} @ {self.collected_at.isoformat()}"

class Process(models.Model):
    snapshot = models.ForeignKey(Snapshot, on_delete=models.CASCADE, related_name='processes')
    pid = models.IntegerField()
    ppid = models.IntegerField()
    name = models.CharField(max_length=255)
    cpu_percent = models.FloatField()
    mem_rss = models.BigIntegerField()
    mem_vms = models.BigIntegerField()

    class Meta:
        indexes = [
            models.Index(fields=['snapshot', 'ppid']),
            models.Index(fields=['snapshot', 'pid'])
        ]

    def __str__(self):
        return f"{self.name} ({self.pid})"
