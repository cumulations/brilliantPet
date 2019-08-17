from django.db import models
from brilliantPet.generalMethods import generalClass
from django.core.exceptions import *
import traceback



gm = generalClass()


salt = "(UmU|@T!0N5T3(hN0|0g!35"
defaultProfileImage = "https://s3.us-east-2.amazonaws.com/brilliantpet.images/1_1560301349979.0452.jpeg"
petDefaultImage = "https://s3.us-east-2.amazonaws.com/brilliantpet.images/1_1560325598428.9006.png"


class MachineDetails(models.Model):
    machine_id = models.CharField(primary_key=True, max_length=100)
    userid = models.ForeignKey('User', models.DO_NOTHING, db_column='userid', blank=False, null=False)
    mode = models.CharField(max_length=100, blank=False, null=False)
    firmware = models.CharField(max_length=100, blank=False, null=False, default = "1.1.1")
    network = models.TextField(blank=False, null=False)
    name = models.CharField(max_length=100, blank=False, null=False)
    isremoved = models.IntegerField(blank=False, null=False)
    status = models.IntegerField(blank=False, null=False, default = 1)
    user_role = models.CharField(max_length=25, blank=False, null=False)




class User(models.Model):
    userid = models.CharField(primary_key=True, max_length=100)
    email = models.CharField(max_length=50, blank=False, null=False)
    address = models.TextField(blank=False, null=False)
    name = models.CharField(max_length=50, blank=False, null=False)
    profile_image = models.TextField(blank=False, null=False, default=defaultProfileImage)
    rolls_count_at_home = models.IntegerField(blank=False, null=False)
    password = models.CharField(max_length = 512, null = False, blank = False)
    login_token = models.CharField(max_length=256, null = True, blank = True)
    shopify_access_token = models.CharField(max_length=256, null = False, blank = False, default="shouldBeFilled")
    notificationToken = models.CharField(max_length=200, null = False, blank = False, default = "toBeFilled")
    isDeleted = models.IntegerField(blank = False, null = False, default = 0)




class Pets(models.Model):

    petid = models.AutoField(primary_key=True)

    userid = models.ForeignKey(User, on_delete=models.CASCADE, null = False, blank=False)
    name = models.CharField(max_length=45, null = False, blank = False)
    breed = models.CharField(max_length=45, null = False, blank=False)
    birthday = models.DateField(null=False)
    image_url = models.TextField(null = False, default = petDefaultImage)
    weight = models.IntegerField(null = False)
    weight_unit = models.CharField(max_length=45, null = False)
    is_deleted = models.IntegerField(null = False, blank=False, default=0)




class events(models.Model):

    eventid = models.AutoField(primary_key=True)

    type = models.CharField(max_length=45, null = False)
    date = models.DateTimeField(auto_now_add=True)
    value = models.TextField(null = False, blank = False)
    machine_id = models.ForeignKey(MachineDetails, on_delete=models.CASCADE, null= False, blank = False)
    userid = models.ForeignKey(User, on_delete=models.CASCADE, null = False, blank = False)

    # def __str__(self):
    #
    #     return str({
    #         "eventid" : self.eventid,
    #         "date" : self.date,
    #         "value" : self.value,
    #         "type" : self.type
    #     })




class notification_token(models.Model):

    id = models.AutoField(primary_key=True)

    userid = models.ForeignKey(User, on_delete=models.CASCADE, null = False, blank = False)
    token = models.CharField(max_length=200, null = False, blank = False)
    dev_type = models.CharField(max_length=15, null = False, blank = False)



class device_info(models.Model):

    machine_id = models.ForeignKey(MachineDetails, on_delete=models.CASCADE, null = False, blank = False)

    mark_count = models.IntegerField(null = False, blank = False, default = 0)
    camera_framesize = models.IntegerField(null = False, blank = False)
    quality = models.IntegerField(null = False, blank = False)





















# Create your models here