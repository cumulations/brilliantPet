# Generated by Django 2.1.7 on 2019-06-12 07:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_pets_is_deleted'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pets',
            name='image_url',
            field=models.TextField(default='https://s3.us-east-2.amazonaws.com/brilliantpet.images/1_1560325598428.9006.png'),
        ),
    ]
