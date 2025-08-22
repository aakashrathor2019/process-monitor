from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Machine',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('hostname', models.CharField(max_length=255, unique=True)),
                ('api_key', models.CharField(max_length=255)),
                ('last_seen', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Snapshot',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('collected_at', models.DateTimeField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('machine', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='snapshots', to='monitor.machine')),
            ],
            options={
                'indexes': [models.Index(fields=['machine', '-collected_at'], name='monitor_sna_machine_c2b2b6_idx')],
            },
        ),
        migrations.CreateModel(
            name='Process',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pid', models.IntegerField()),
                ('ppid', models.IntegerField()),
                ('name', models.CharField(max_length=255)),
                ('cpu_percent', models.FloatField()),
                ('mem_rss', models.BigIntegerField()),
                ('mem_vms', models.BigIntegerField()),
                ('snapshot', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='processes', to='monitor.snapshot')),
            ],
            options={
                'indexes': [
                    models.Index(fields=['snapshot', 'ppid'], name='monitor_pro_snapshot_c7a0f8_idx'),
                    models.Index(fields=['snapshot', 'pid'], name='monitor_pro_snapshot_5e6f0f_idx'),
                ],
            },
        ),
    ]
