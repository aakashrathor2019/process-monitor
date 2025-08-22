from django.urls import path
from . import views

urlpatterns = [
    path("ingest", views.ingest, name="ingest"),
    path("hosts", views.hosts, name="hosts"),
    path("snapshots/latest", views.latest_snapshot, name="latest_snapshot"),
]
