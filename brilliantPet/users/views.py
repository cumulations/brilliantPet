from django.shortcuts import render
import json
import traceback
from .models import MachineDetails, User, Pets
from django.core.exceptions import *
from rest_framework.views import APIView
from django.db import IntegrityError
from brilliantPet.generalMethods import *
from brilliantPet import settings
import boto3
import base64
import time
from .userFunctions import *

gm = generalClass()

class notFound(APIView):

    def get(self, request):
        message = "Service not found."
        return gm.clientError(message)



class userDevices(APIView):

    def get(self, request):

        machines = []
        params = request.query_params

        hasError = authenticate(params)
        if hasError:
            return hasError

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

        data = request.data

        hasError = authenticate(data)
        if hasError:
            return hasError

        requiredParams = ["machine_id", "name", "status", "mode", "firmware", "network", "user_role"]

        missingParams = gm.missingParams(requiredParams, data)
        if missingParams:
            missingParams = ", ".join(missingParams)
            return gm.clientError(missingParamMessage.format(missingParams))

        emptyParams = gm.emptyParams(requiredParams, data)
        if emptyParams:
            emptyParams = ", ".join(emptyParams)
            return gm.clientError(emptyParamMessage.format(emptyParams))

        try:
            MachineDetails.objects.get(pk = data["machine_id"])
            return gm.clientError("machine_id exists. Please provide a unique machine_id")
        except:
            machineid = data["machine_id"].strip()
            userid = data["userid"].strip()
            name = data["name"].strip()
            status = int(data["status"].strip())

        defaultParams = {
            "mode" : "manual",
            "firmware" : "",
            "network" : "",
            "isremoved" : 0,
            "user_role" : "owner"
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
            user = getUser(data)
            user.machinedetails_set.create(machine_id = machineid, name = name, status = status, \
                                     mode = mode, firmware = firmware, network = network, isremoved = isRemoved,\
                                     user_role = user_role)
        except Exception as e:
            traceback.print_exc()
            return gm.errorResponse("Error while saving device details.")

        else:
            return gm.successResponse(data)



class usersView(APIView):
    bucketName = "brilliantpet.user-images"

    def get(self, request):
        params = request.query_params
        gm.log(params)

        hasError = authenticate(params)
        if hasError:
            return hasError

        user = getUser(params)

        data = {
            "email" : user.email,
            "name" : user.name,
            "address" : user.address,
            "rolls_count_at_home" : user.rolls_count_at_home,
            "userid" : user.userid,
            "profile_image" : user.profile_image,
        }
        return gm.successResponse(data)

    def post(self, request):
        data = request.data
        requiredParams = ["userid", "name", "notification_token", "rolls_count_at_home", "password", "email", "address"]
        data = gm.cleanData(data)
        data["profile_image"] = ""

        missingParams = gm.missingParams(requiredParams, data)
        if missingParams:
            missingParams = ", ".join(missingParams)
            return gm.clientError(missingParamMessage.format(missingParams))

        emptyParams = gm.emptyParams(requiredParams, data)
        if emptyParams:
            emptyParams = ", ".join(emptyParams)
            return gm.clientError(emptyParamMessage.format(emptyParams))

        if "rolls_count_at_home" in data:
            try:
                int(data["rolls_count_at_home"])
            except:
                return gm.clientError("rolls_count_at_home should be int.")




        #uploading profile Image

        imageHandler = request.FILES.get("profile_image")
        if imageHandler:
            extension = gm.getFileExtension(imageHandler.name)
            fileName = gm.getUniqueFileName(extension)
            image = imageHandler.read()
            mimetype = "image/jpeg"

            downloadUrl = gm.uploadToS3(self.bucketName, fileName, image, mimetype)

            if downloadUrl:
                data["profile_image"] = downloadUrl     #setting profile image if upload success

        # default profile image if upload failed


        if isUser(data):
            return gm.clientError("User already exists.")

        else:
            try:
                user = register(data)
                details = {
                    "userid" : user.userid,
                    "name" : user.name,
                    "notification_token" : user.notification_token,
                    "rolls_count_at_home" : user.rolls_count_at_home,
                    "email" : user.email,
                    "address" : user.address,
                    "profile_image" : user.profile_image
                }
                return gm.successResponse(details)

            except ValidationError as e:
                return gm.errorResponse(str(e))

            except:
                gm.errorLog(traceback.format_exc())
                return gm.errorResponse("Error while adding user.")



class imageUploadMultipart(APIView):

    bucketName = "brilliantpet.user-images"

    def get(self, request):

        return gm.clientError("GET method is not supported.")


    def post(self, request):

        imageHandler = request.FILES.get('image_file')
        if not imageHandler:
            return gm.clientError("Required param image_file missing in form-data.")

        data = request.data

        hasError = authenticate(data)
        if hasError:
            return hasError

        userid = getUser(data).userid
        imgtype = gm.getFileExtension(imageHandler.name)
        fileName = "{}_{}".format(userid, gm.getUniqueFileName(imgtype))
        mimetype = "image/jpeg"
        image = imageHandler.read()

        download_url = gm.uploadToS3(self.bucketName, fileName, image, mimetype)

        if download_url:
            gm.log("Image received : {}".format(image) + "\nUrl generated : " + download_url)
            return gm.successResponse(download_url)

        else:
            return gm.clientError("Error while uploading file.")



class userLogin(APIView):

    def get(self, request):
        return gm.clientError("GET Method is not supported.")

    def post(self, request):
        data = request.data

        missingLoginDetails = gm.login_details_absent(data)
        if not missingLoginDetails:
            return missingLoginDetails

        if "password" not in data:
            return gm.clientError("Required param 'password' missing.")

        user = isUser(data)

        if not user:
            return gm.not_a_user()

        token = login(data, user)

        if token:
            loginToken = {
                "login_token" : token
            }
            return gm.successResponse(loginToken)

        else:
            return gm.clientError("Invalid userid/email or password.")


class userLogout(APIView):

    def get(self, request):
        return gm.clientError("GET Method is not supported.")

    def post(self, request):

        data = request.data
        hasError = authenticate(data)
        if hasError:
            return hasError

        user = getUser(data)

        if logout(data, user):
            return gm.successResponse("Successfully logged out.")

        else:
            return gm.errorResponse("Couldn't log out user.")




class pets(APIView):

    def get(self, request):
        pets = []
        params = request.query_params

        hasError = authenticate(params)
        if hasError:
            return hasError


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
        requiredParams = [ "name", "breed", "birthday", "image_url", "weight", "weight_unit"]
        data = gm.cleanData(request.data)

        hasError = authenticate(data)
        if hasError:
            return hasError

        missingParams = gm.missingParams(requiredParams, data)
        if missingParams:
            missingParams = ", ".join(missingParams)
            return gm.clientError(missingParamMessage.format(missingParams))

        requiredParams.pop(3)

        emptyParams = gm.emptyParams(requiredParams, data)
        if emptyParams:
            emptyParams = ", ".join(emptyParams)
            return gm.clientError((emptyParamMessage.format(emptyParams)))

        user = getUser(data)

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
            gm.errorLog(traceback.format_exc())
            return gm.errorResponse("Error while saving device details.")

        else:
            data["petid"] = pet.petid
            data["image_url"] = pet.image_url
            return gm.successResponse(data)



    def put(self, request):

        data = gm.cleanData(request.data)

        hasError = authenticate(data)
        if hasError:
            return hasError

        requiredParams = ["petid"]
        missingParams = gm.missingParams(requiredParams, data)
        if missingParams:
            missingParams = ", ".join(missingParams)
            return gm.clientError(missingParamMessage.format(missingParams))

        changeable = ["petid", "name", "breed", "birthday", "image_url", "weight", "weight_unit"]
        emptyParams = gm.emptyParams(changeable, data)
        if emptyParams:
            emptyParams = ", ".join(emptyParams)
            return gm.clientError(emptyParamMessage.format(emptyParams))

        user = getUser(data)
        pet = user.pets_set.filter(petid = data["petid"], is_deleted = 0)

        if not pet:
            return gm.clientError("Invalid petid.")

        pet = pet[0]
        try:
            pet = gm.change(pet, data, changeable)

            returnDict = {}
            for item in changeable:
                returnDict[item] = getattr(pet, item)

            return gm.successResponse(returnDict)



        except:
            traceback.print_exc()
            gm.errorLog(traceback.format_exc())
            return gm.errorResponse("There was some error while making changes. Try again later.")


    def delete(self, request):

        data = gm.cleanData(request.data)

        hasError = authenticate(data)
        if hasError:
            return hasError

        requiredParams = ["petid"]
        emptyOrMissing = gm.getMissingEmptyParams(requiredParams, data)

        if emptyOrMissing:
            return emptyOrMissing

        try:
            pet = Pets.objects.get(petid = data["petid"], is_deleted = 0)

        except Pets.DoesNotExist:
            return gm.clientError("Invalid petid.")

        except :
            traceback.print_exc()
            gm.errorLog(traceback.format_exc())
            return gm.errorResponse("Could not verify petid due to some error.")

        else:
            pet.is_deleted = 1
            pet.save()
            return gm.successResponse("Pet with petid : {} successfully deleted.".format(pet.petid))





















































