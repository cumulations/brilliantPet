from django.db import models


class MachineDetails(models.Model):
    machine_id = models.CharField(primary_key=True, max_length=100)
    userid = models.ForeignKey('User', models.DO_NOTHING, db_column='userid', blank=True, null=True)
    mode = models.CharField(max_length=100, blank=True, null=True)
    firmware = models.CharField(max_length=100, blank=True, null=True)
    network = models.TextField(blank=True, null=True)
    name = models.CharField(max_length=100, blank=True, null=True)
    isremoved = models.IntegerField(blank=True, null=True)
    status = models.IntegerField(blank=True, null=True)
    user_role = models.CharField(max_length=25, blank=True, null=True)




class User(models.Model):
    userid = models.CharField(primary_key=True, max_length=100)
    email = models.CharField(max_length=50, blank=False, null=False)
    address = models.TextField(blank=False, null=False)
    name = models.CharField(max_length=50, blank=False, null=False)
    profile_image = models.TextField(blank=True, null=True)
    notification_token = models.CharField(max_length=145, blank=True, null=True)
    rolls_count_at_home = models.IntegerField(blank=True, null=True)




# Create your models here