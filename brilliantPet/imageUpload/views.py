from django.shortcuts import render
import json
import traceback
from django.core.exceptions import *
from rest_framework.views import APIView
from django.db import IntegrityError
from brilliantPet.generalMethods import *
from brilliantPet import settings
import boto3
import base64
import time

gm = generalClass()
bucketName = "brilliantpet.images"


def generate_url(fileName):
    baseUrl = "https://s3.{}.amazonaws.com/{}/{}"
    return baseUrl.format(region_name, bucketName, fileName)


class imageUpload_base64(APIView):

    def get(self, request):

        return gm.clientError("GET method is not supported.")


    def post(self, request):

        data = request.data


        requiredParams = ["image_file"]
        missingParams = gm.missingParams(requiredParams, data)
        if missingParams:
            missingParams = ", ".join(missingParams)
            return gm.clientError(missingParamMessage.format(missingParams))

        emptyParams = gm.emptyParams(requiredParams, data)
        if emptyParams:
            emptyParams = ", ".join(emptyParams)
            return gm.clientError(emptyParamMessage.format(emptyParams))

        imgtype = "jpeg"

        randomString = gm.randomStringGenerator(5)

        b64body = data['image_file']
        image = base64.b64decode(b64body)

        s3 = gm.getS3resource()
        try:
            mimetype = "image/jpeg"
            folder = s3.Bucket(bucketName)
            ct = int(time.time() * 100000)
            fileName = "{}_{}.{}".format(randomString, ct, imgtype)
            i = folder.put_object(Key=fileName, Body=image, ACL='public-read', ContentType = mimetype)
            download_url = generate_url(fileName)
            gm.log("b64body received : " + str(b64body) + "\nUrl generated : " + download_url)

            return gm.successResponse(download_url)

        except:
            traceback.print_exc()
            gm.errorLog(traceback.format_exc())
            return gm.clientError("Error while uploading file.")



class imageUpload(APIView):

    def get(self, request):
        return gm.clientError("GET method is not supported.")



    def post(self, request):

        imageHandler = request.FILES.get('image_file')
        print(request.data)
        gm.log(event = request.data)
        if not imageHandler:
            return gm.clientError("Required param image_file missing in form-data.")

        imgName = ".".join(imageHandler.name.split(".")[:-1])
        imgType = gm.getFileExtension(imageHandler.name)
        fileName = "{}_{}".format(imgName, gm.getUniqueFileName(imgType))
        mimetype = "image/jpeg"
        image = imageHandler.read()

        download_url = gm.uploadToS3(bucketName, fileName, image, mimetype)
        if download_url :
            gm.log("Image received : {}".format(image) + "\nUrl generated : " + download_url)
            return gm.successResponse(download_url)

        else:
            return gm.clientError("Error while uploading file.")
