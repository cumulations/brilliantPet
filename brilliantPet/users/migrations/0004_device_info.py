# Generated by Django 2.1.7 on 2019-08-19 03:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_auto_20190819_0332'),
    ]

    operations = [
        migrations.CreateModel(
            name='device_info',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mark_count', models.IntegerField(default=0)),
                ('camera_framesize', models.IntegerField()),
                ('quality', models.IntegerField()),
                ('machine_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.MachineDetails')),
            ],
        ),
    ]
