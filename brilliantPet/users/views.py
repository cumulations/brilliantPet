from django.shortcuts import render
import json
import traceback
from .models import MachineDetails, User, Pets, petDefaultImage
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

        hasError = hasErrorAuthenticate(params)
        if hasError:
            return hasError

        else:
            user = getUser(params)
            if user.user_type.lower() in ["admin", "customer_support"]:
                userMachines = MachineDetails.objects.filter(isremoved = 0)
            else:
                userMachines = MachineDetails.objects.filter(userid = params["userid"], isremoved = 0)
            for m in userMachines:
                machine = {
                    "machine_id" : m.machine_id,
                    "mode" : m.mode,
                    "name" : m.name,
                    "status" : m.status,
                    "userid" : m.userid_id
                }
                machines.append(machine)

            return gm.successResponse(machines)


    def post(self, request):

        data = request.data

        hasError = hasErrorAuthenticate(data)
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

        # try:
        #     MachineDetails.objects.get(pk = data["machine_id"], isremoved = 0)
        #     return gm.clientError("machine_id exists. Please provide a unique machine_id")
        # except:
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

        user = getUser(data)

        try:

            user.machinedetails_set.create(machine_id = machineid, name = name, status = status, \
                                     mode = mode, firmware = firmware, network = network, isremoved = isRemoved,\
                                     user_role = user_role)

        except  IntegrityError as e:
            machine = MachineDetails.objects.get(pk = data["machine_id"])
            machine.machine_id = machineid
            machine.name = name
            machine.userid = user
            machine.status = status
            machine.mode = mode
            machine.firmware = firmware
            machine.network = network
            machine.isremoved = isRemoved
            machine.user_role = user_role

            machine.save()

            return gm.successResponse(data)


        except Exception as e:
            traceback.print_exc()
            gm.errorLog(traceback.format_exc())
            return gm.errorResponse("Error while saving device details.")

        else:
            return gm.successResponse(data)



    def delete(self, request):

        data = gm.cleanData(request.data)

        hasError = hasErrorAuthenticate(data)
        if hasError:
            return hasError

        requiredParams = ["machine_id"]
        emptyOrMissing = gm.getMissingEmptyParams(requiredParams, data)

        if emptyOrMissing:
            return emptyOrMissing
        try:
            machine = MachineDetails.objects.get(machine_id = data["machine_id"])
            machine.isremoved = 1
            machine.save()
            return gm.successResponse("Successfully deleted mahine : {}".format(machine.machine_id))

        except:
            error = traceback.format_exc()
            print(error)
            gm.errorLog(error)
            return gm.errorResponse("There was a problem while deleting the machine.")




class usersView(APIView):
    bucketName = "brilliantpet.user-images"

    def get(self, request):
        params = request.query_params
        gm.log(params)

        hasError = hasErrorAuthenticate(params)
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
        requiredParams = ["userid", "name", "notification_token", "rolls_count_at_home", "password", "email", "address", "shopify_access_token"]
        data = gm.cleanData(data)
        data["profile_image"] = ""

        if data["notification_token"] in ["", " ", None, False]:
            data["notification_token"] = "default_Notification_token"

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

        user = isUser(data)

        try:
            user = register(data, user)
            token = login(data, user)
            details = {
                "userid" : user.userid,
                "name" : user.name,
                "notification_token" : user.notificationToken,
                "rolls_count_at_home" : user.rolls_count_at_home,
                "email" : user.email,
                "address" : user.address,
                "profile_image" : user.profile_image,
                "shopify_access_token" : user.shopify_access_token,
                "login_token" : token
            }
            return gm.successResponse(details)

        except ValidationError as e:
            return gm.errorResponse(str(e))

        except:
            gm.errorLog("Data : {}\nError : {}".format(data, traceback.format_exc()))

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

        hasError = hasErrorAuthenticate(data)
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
        hasError = hasErrorAuthenticate(data)
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

        hasError = hasErrorAuthenticate(params)
        if hasError:
            return hasError


        else:
            user = getUser(params)
            if user.user_type.lower() in ["admin", "customer_support"]:
                userPets = Pets.objects.filter(is_deleted = 0)
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
                    "birthday" : m.birthday,
                    "userid" : m.userid_id
                }
                pets.append(pet)

            return gm.successResponse(pets)


    def post(self, request):
        requiredParams = [ "name", "breed", "birthday", "image_url", "weight", "weight_unit"]
        data = gm.cleanData(request.data)

        hasError = hasErrorAuthenticate(data)
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
            if data["image_url"] not in ["", None]:
                imageUrl = data["image_url"]
            else:
                imageUrl = petDefaultImage

            pet = user.pets_set.create(name = data["name"],\
                       breed = data["breed"], birthday = data["birthday"],\
                       weight = data["weight"],\
                       weight_unit = data["weight_unit"], image_url = imageUrl)

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

        gm.errorLog("This")

        data = gm.cleanData(request.data)

        hasError = hasErrorAuthenticate(data)
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

        hasError = hasErrorAuthenticate(data)
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



class notificationUpdate(APIView):

    def post(self, request):
        gm.log(dir(request))
        data = gm.cleanData(request.data)
        gm.log(data)
        gm.log(request.query_params)
        hasError = hasErrorAuthenticate(data)
        if hasError:
            return hasError

        requiredParams = ["notification_token", "dev_type"]
        emptyOrMissing = gm.getMissingEmptyParams(requiredParams, data)

        if emptyOrMissing:
            return emptyOrMissing

        user = getUser(data)
        tokenAdded = addNotificationToken(data, user)

        if tokenAdded:
            return gm.successResponse("notification_token updated successfully.")

        else:
            return gm.errorResponse("There was an error while updating notification_token")




class Event(APIView):

    def get(self, request):

        params = gm.cleanData(request.query_params)
        hasError = hasErrorAuthenticate(params)
        if hasError:
            return hasError

        requiredParams = ["userid", "machine_id", "startDate", "endDate"]
        emptyOrMissing = gm.getMissingEmptyParams(requiredParams, params)

        if emptyOrMissing:
            return emptyOrMissing

        startDate = params["startDate"]
        endDate = params["endDate"]

        try:
            user = getUser(params)
            if user.user_type.lower() in ["admin", "customer_support"]:
                ev = events.objects.filter(date__range = (startDate, endDate), machine_id = params["machine_id"]).order_by("-date")
            else:
                ev = events.objects.filter(date__range = (startDate, endDate), machine_id = params["machine_id"], userid = params["userid"]).order_by("-date")


            retSet = []

            for item in ev:
                retSet.append({
                "eventid" : item.eventid,
                "date" : item.date,
                "value" : item.value,
                "type" : item.type
            })


            return gm.successResponse(retSet)

        except:
            traceback.print_exc()
            gm.errorLog(traceback.format_exc())
            return gm.errorResponse("There was some error generating response")


class LastEventOfTheMachine(APIView):

     def get(self, request):

        params = gm.cleanData(request.query_params)
        hasError = hasErrorAuthenticate(params)
        if hasError:
            return hasError

        requiredParams = ["userid", "machine_id"]
        emptyOrMissing = gm.getMissingEmptyParams(requiredParams, params)

        if emptyOrMissing:
            return emptyOrMissing

        impEvents = [ "LOOKIN", "ANIMAL_DETECTION", "conStatus"]

        try:
            user = getUser(params)
            if user.user_type.lower() in ["admin", "customer_support"]:
                ev = events.objects.filter (type__in=impEvents, machine_id = params["machine_id"], userid = params["userid"]).order_by("-date")[:1] 
            else:
                ev = events.objects.filter (type__in=impEvents, machine_id = params["machine_id"], userid = params["userid"]).order_by("-date")[:1] 


            retSet = []

            for item in ev:
                retSet.append({
                "eventid" : item.eventid,
                "date" : item.date,
                "value" : item.value,
                "type" : item.type
            })


            return gm.successResponse(retSet)

        except:
            traceback.print_exc()
            gm.errorLog(traceback.format_exc())
            return gm.errorResponse("There was some error generating response")
































































