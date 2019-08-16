# Generated by Django 2.1.7 on 2019-08-16 03:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_auto_20190706_1050'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='notificationToken',
            field=models.CharField(default='toBeAdded', max_length=200),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='user',
            name='shopify_access_token',
            field=models.CharField(default='toBeFilled', max_length=512),
            preserve_default=False,
        ),
    ]
