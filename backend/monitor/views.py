from django.db import transaction
from django.utils.timezone import make_aware
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .models import Machine, Snapshot, Process
from .serializers import IngestSerializer

def authenticate(request):
    key = request.headers.get("X-API-Key")
    return key

@api_view(["POST"])
def ingest(request):
    api_key = authenticate(request)
    if not api_key:
        return Response({"detail": "Missing X-API-Key"}, status=status.HTTP_401_UNAUTHORIZED)

    ser = IngestSerializer(data=request.data)
    ser.is_valid(raise_exception=True)

    hostname = ser.validated_data["hostname"]
    collected_at = ser.validated_data["collected_at"]
    if collected_at.tzinfo is None:
        collected_at = make_aware(collected_at)

    machine, created = Machine.objects.get_or_create(hostname=hostname, defaults={"api_key": api_key})
    if not created and machine.api_key != api_key:
        return Response({"detail": "Invalid API key for host"}, status=status.HTTP_403_FORBIDDEN)

    with transaction.atomic():
        snap = Snapshot.objects.create(machine=machine, collected_at=collected_at)
        Process.objects.bulk_create([
            Process(snapshot=snap,
                    pid=p["pid"], ppid=p["ppid"], name=p["name"],
                    cpu_percent=p["cpu_percent"], mem_rss=p["mem_rss"], mem_vms=p["mem_vms"])
            for p in ser.validated_data["processes"]
        ])
        machine.last_seen = collected_at
        machine.save(update_fields=["last_seen"])

    return Response({"status": "ok", "snapshot_id": snap.id})

@api_view(["GET"])
def hosts(request):
    data = list(Machine.objects.order_by("hostname").values_list("hostname", flat=True))
    return Response({"hosts": data})

def build_tree(processes):
    by_pid = {p["pid"]: {**p, "children": []} for p in processes}
    roots = []
    for p in by_pid.values():
        parent = by_pid.get(p["ppid"])
        if parent and p["pid"] != p["ppid"]:
            parent["children"].append(p)
        else:
            roots.append(p)
    def sort_tree(node):
        node["children"].sort(key=lambda x: (x["name"].lower(), x["pid"]))
        for c in node["children"]:
            sort_tree(c)
    for r in roots:
        sort_tree(r)
    return roots

@api_view(["GET"])
def latest_snapshot(request):
    hostname = request.GET.get("hostname")
    if not hostname:
        return Response({"detail": "hostname is required"}, status=400)

    try:
        m = Machine.objects.get(hostname=hostname)
    except Machine.DoesNotExist:
        return Response({"detail": "host not found"}, status=404)

    snap = m.snapshots.order_by("-collected_at", "-id").first()
    if not snap:
        return Response({"detail": "no data"}, status=404)

    procs = list(snap.processes.values("pid","ppid","name","cpu_percent","mem_rss","mem_vms"))
    tree = build_tree(procs)
    return Response({
        "hostname": m.hostname,
        "collected_at": snap.collected_at.isoformat(),
        "process_tree": tree
    })
