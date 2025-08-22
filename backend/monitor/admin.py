from django.contrib import admin
from .models import Machine, Snapshot, Process

admin.site.register(Machine)
admin.site.register(Snapshot)
admin.site.register(Process)
