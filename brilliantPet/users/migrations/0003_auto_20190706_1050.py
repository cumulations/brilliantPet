# Generated by Django 2.1.7 on 2019-07-06 10:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_auto_20190705_1323'),
    ]

    operations = [
        migrations.RenameField(
            model_name='events',
            old_name='eventit',
            new_name='eventid',
        ),
    ]