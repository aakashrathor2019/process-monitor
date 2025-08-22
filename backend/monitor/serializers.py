from rest_framework import serializers

class IngestProcessSerializer(serializers.Serializer):
    pid = serializers.IntegerField()
    ppid = serializers.IntegerField()
    name = serializers.CharField()
    cpu_percent = serializers.FloatField()
    mem_rss = serializers.IntegerField()
    mem_vms = serializers.IntegerField()

class IngestSerializer(serializers.Serializer):
    hostname = serializers.CharField()
    collected_at = serializers.DateTimeField()
    processes = IngestProcessSerializer(many=True)
