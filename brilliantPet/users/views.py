from django.shortcuts import render
import json
import traceback
from .models import MachineDetails, User, Pets
from rest_framework.views import APIView
from django.db import IntegrityError
from brilliantPet import generalMethods
from brilliantPet import settings
import boto3
import base64
import time


aws_access_key_id = settings.aws_access_key_id
aws_secret_access_key = settings.aws_secret_access_key
region_name = settings.region_name


gm = generalMethods.generalClass()
missingParamMessage = "({}) missing in post data."
emptyParamMessage = "({}) empty in post data."



class notFound(APIView):

    def get(self, request):
        message = "Service not found."
        return gm.clientError(message)



class userDevices(APIView):

    def get(self, request):

        machines = []
        params = request.query_params
        if "userid" not in params:
            return gm.clientError("Required param 'userid' missing.")

        try:
            user = User.objects.get(pk = params["userid"])
        except:
            return gm.clientError("User does not exist.")
        else:
            userMachines = MachineDetails.objects.filter(userid = params["userid"], isremoved = 0)
            for m in userMachines:
                machine = {
                    "machine_id" : m.machine_id,
                    "mode" : m.mode,
                    "name" : m.name,
                    "status" : m.status
                }
                machines.append(machine)

            return gm.successResponse(machines)


    def post(self, request):
        requiredParams = ["machine_id", "userid", "name", "status"]
        data = request.data

        missingParams = gm.missingParams(requiredParams, data)
        if missingParams:
            missingParams = ", ".join(missingParams)
            return gm.clientError(missingParamMessage.format(missingParams))

        emptyParams = gm.emptyParams(requiredParams, data)
        if emptyParams:
            emptyParams = ", ".join(emptyParams)
            return gm.clientError((emptyParamMessage.format(emptyParams)))

        try:
            user = User.objects.get(pk = data['userid'])
        except:
            return gm.clientError("User doesn't exist.")

        try:
            MachineDetails.objects.get(pk = data["machine_id"])
            return gm.clientError("machine_id exists. Please provide a unique machine_id")
        except:
            machineid = data["machine_id"].strip()
            userid = data["userid"].strip()
            name = data["name"].strip()
            status = int(data["status"].strip())

        defaultParams = {
            "mode" : "",
            "firmware" : "",
            "network" : "",
            "isremoved" : 0,
            "user_role" : ""
        }

        for default in defaultParams.keys():
            if default in data:
                defaultParams[default] = data[default]

        mode = defaultParams["mode"]
        firmware = defaultParams["firmware"]
        network = defaultParams["network"]
        isRemoved = defaultParams["isremoved"]
        user_role = defaultParams['user_role']


        try:

            user.machinedetails_set.create(machine_id = machineid, name = name, status = status, \
                                     mode = mode, firmware = firmware, network = network, isremoved = isRemoved,\
                                     user_role = user_role)
        except Exception as e:
            traceback.print_exc()
            return gm.errorResponse("Error while saving device details.")

        else:
            return gm.successResponse(data)



class usersView(APIView):

    def get(self, request):
        params = request.query_params
        if "userid" not in params:
            return gm.clientError("Required param 'userid' missing.")

        try:
            user = User.objects.get(pk = params["userid"])
        except:
            return gm.clientError("User does not exist.")
        else:
            data = {
                "email" : user.email,
                "name" : user.name,
                "address" : user.address,
                "rolls_count_at_home" : user.rolls_count_at_home
            }
            return gm.successResponse(data)

    def post(self, request):
        data = request.data
        requiredParams = ["userid", "email", "address", "name"]

        missingParams = gm.missingParams(requiredParams, data)
        if missingParams:
            missingParams = ", ".join(missingParams)
            return gm.clientError(missingParamMessage.format(missingParams))

        emptyParams = gm.emptyParams(requiredParams, data)
        if emptyParams:
            emptyParams = ", ".join(emptyParams)
            return gm.clientError((emptyParamMessage.format(emptyParams)))

        if "rolls_count_at_home" in data:
            try:
                int(data["rolls_count_at_home"])
            except:
                return gm.clientError("rolls_count_at_home should be int.")

        cleanedData = gm.cleanData(data)

        try:
            user = User.objects.get(pk = cleanedData["userid"])
            return gm.clientError("User already exists.")

        except:

            em = User.objects.filter(email = cleanedData["email"])
            if len(em) > 0:
                return gm.clientError("Email address already exists.")

            defaultParams = {
                "rolls_count_at_home" : 0,
                "notification_token" : None,
                "profile_image": None
            }

            for param in defaultParams:
                if param in data:
                    cleanedData[param] = data[param]
                else:
                    cleanedData[param] = defaultParams[param]


            user = User()
            user.userid = cleanedData["userid"]
            user.email = cleanedData["email"]
            user.name = cleanedData["name"]
            user.address = cleanedData["address"]
            user.rolls_count_at_home = cleanedData["rolls_count_at_home"]
            user.notification_token = cleanedData["notification_token"]
            user.profile_image = cleanedData["profile_image"]

            try:
                user.save()
                details = {
                    "userid" : cleanedData["userid"],
                    "email" : cleanedData["email"],
                    "name" : cleanedData["name"],
                    "address" : cleanedData["address"],
                    "rolls_count_at_home" : cleanedData["rolls_count_at_home"]
                }
                return gm.successResponse(details)

            except:
                gm.log(traceback.format_exc())
                return gm.errorResponse("Error while adding user.")

#something



class imageUpload(APIView):

    bucketName = "brilliantpet.images"

    def generate_url(self, fileName):
        baseUrl = "https://s3.{}.amazonaws.com/{}/{}"
        return baseUrl.format(region_name, self.bucketName, fileName)

    def get(self, request):

        return gm.clientError("GET method is not supported.")


    def post(self, request):

        data = request.data
        requiredParams = ["imgtype", "b64body", "userid"]

        missingParams = gm.missingParams(requiredParams, data)
        if missingParams:
            missingParams = ", ".join(missingParams)
            return gm.clientError(missingParamMessage.format(missingParams))

        emptyParams = gm.emptyParams(requiredParams, data)
        if emptyParams:
            emptyParams = ", ".join(emptyParams)
            return gm.clientError((emptyParamMessage.format(emptyParams)))

        user = data["userid"][0]
        b64body = data["b64body"][0]
        imgtype = data["imgtype"]


        try:
            User.objects.get(pk = user)
        except:
            gm.log(traceback.format_exc())
            return gm.clientError("User does not exist.")

        b64body = data['b64body']
        image = base64.b64decode(b64body)

        s3 = boto3.resource("s3", aws_access_key_id = aws_access_key_id, aws_secret_access_key = aws_secret_access_key, region_name = region_name)
        bucket = s3.Bucket("brilliantPet.images")
        try:
            mimetype = "image/jpeg"
            folder = s3.Bucket("brilliantpet.images")
            ct = float(time.time()) * 1000
            fileName = "{}_{}.{}".format(user, ct, imgtype)
            i = folder.put_object(Key=fileName, Body=image, ACL='public-read', ContentType = mimetype)
            download_url = self.generate_url(fileName)
            gm.log("b64body received : " + str(b64body) + "\nUrl generated : " + download_url)

            return gm.successResponse(download_url)


        except:
            traceback.print_exc()
            return gm.clientError("Error while uploading file.")



class pets(APIView):

    def get(self, request):
        pets = []
        params = request.query_params
        if "userid" not in params:
            return gm.clientError("Required param 'userid' missing.")

        try:
            user = User.objects.get(pk=params["userid"])
        except:
            return gm.clientError("User does not exist.")
        else:
            userPets = Pets.objects.filter(userid=params["userid"], is_deleted = 0)
            for m in userPets:
                pet = {
                    "petid": m.petid,
                    "name": m.name,
                    "breed": m.breed,
                    "weight": m.weight,
                    "weight_unit" : m.weight_unit,
                    "image_url" : m.image_url,
                    "birthday" : m.birthday
                }
                pets.append(pet)

            return gm.successResponse(pets)


    def post(self, request):
        requiredParams = ["userid", "name", "breed", "birthday", "image_url", "weight", "weight_unit"]
        data = request.data

        missingParams = gm.missingParams(requiredParams, data)
        if missingParams:
            missingParams = ", ".join(missingParams)
            return gm.clientError(missingParamMessage.format(missingParams))

        requiredParams.pop(4)

        emptyParams = gm.emptyParams(requiredParams, data)
        if emptyParams:
            emptyParams = ", ".join(emptyParams)
            return gm.clientError((emptyParamMessage.format(emptyParams)))

        try:
            user = User.objects.get(pk = data['userid'])
        except:
            return gm.clientError("User doesn't exist.")


        data = gm.cleanData(data)
        try:
            pet = user.pets_set.create(name = data["name"],\
                       breed = data["breed"], birthday = data["birthday"],\
                       weight = data["weight"],\
                       weight_unit = data["weight_unit"])

            if data["image_url"] not in ["", None]:
                pet["image_url"] = data["image_url"]
            pet.save()

        except Exception as e:
            traceback.print_exc()
            print("hello")
            return gm.errorResponse("Error while saving device details.")

        else:
            data["petid"] = pet.petid
            data["image_url"] = pet.image_url
            return gm.successResponse(data)


    












