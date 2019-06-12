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
    notification_token = models.CharField(max_length=145, blank=True, null=False)
    rolls_count_at_home = models.IntegerField(blank=False, null=False)
    password = models.CharField(max_length = 512, null = False, blank = False)
    login_token = models.CharField(max_length=256, null = True, blank = True)
    isDeleted = models.IntegerField(blank = False, null = False, default = 0)

    def isLoggedIn(self, data):
        cleanedData = gm.cleanData(data)
        if cleanedData["login_token"] == self.login_token:
            return True

        else:
            return False

    def securePassword(self, password):

        password = str(password) + salt
        password = gm.hash_sha3_512(password)
        return password


    def register(self, data):
        try:
            cleanedData = gm.cleanData(data)
            requiredParams = ["userid", "name", "notification_token", "rolls_count_at_home", \
                              "password", "email", "address"]

            missingParams = gm.missingParams(requiredParams, cleanedData)
            if missingParams:
                raise KeyError("({}) missing.".format(", ".join(missingParams)))

            if len(str(cleanedData["password"])) < 6:
                raise ValueError("Password len too short. Should be more than 6 characters.")

            password = self.securePassword(cleanedData["password"])

            self.userid = cleanedData["userid"]
            self.name = cleanedData["name"]
            self.notification_token = cleanedData["notification_token"]
            self.rolls_count_at_home = cleanedData["rolls_count_at_home"]
            self.password = password
            self.login_token = ""
            self.email = cleanedData["email"]
            self.address = cleanedData["address"]

            self.save()
            return True

        except:
            traceback.print_exc()
            gm.log(traceback.format_exc())
            return False


    def login(self, data):

        try:
            cleanedData = gm.cleanData(data)
            requiredParams = ["email", "password"]

            missingParams = gm.missingParams(requiredParams, cleanedData)
            if missingParams:
                raise KeyError("({}) missing.".format(", ".join(missingParams)))

            password = self.securePassword(cleanedData["password"])
            if cleanedData["email"] == self.email and password == self.password:
                login_token = gm.randomStringGenerator()
                self.login_token = login_token
                self.save()
                return login_token

            else:
                raise ValidationError("email and password doesn't match.")

        except:
            traceback.print_exc()
            gm.log(traceback.format_exc())
            return False


    def authenticate(self, data):

        try:
            cleanedData = gm.cleanData(data)
            requiredParams = ["email", "login_token"]

            missingParams = gm.missingParams(requiredParams, cleanedData)
            if missingParams:
                raise KeyError("({}) missing.".format(", ".join(missingParams)))

            # if self.



        except:
            traceback.print_exc()
            gm.log(traceback.format_exc())

            return False


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


















# Create your models here