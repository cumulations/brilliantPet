from django.shortcuts import render
import json
import traceback
from .models import Training
from django.core.exceptions import *
from rest_framework.views import APIView
from django.db import IntegrityError
from brilliantPet.generalMethods import *
from brilliantPet import settings
import boto3
import base64
import time


# Create your views here.
gm = generalClass()

class trainingView(APIView):

    def get(self, request):

        trainings = Training.objects.filter(is_active = 1)
        data = []
        for training in trainings:
            item = {
                "title" : training.title,
                "link" : training.link,
                "type" : training.type,
                "id" : training.id,
                "created_date" : training.created_date
            }
            data.append(item)

        return gm.successResponse(data)



    def post(self, request):

        data = gm.cleanData(request.data)

        requiredParams = ["title", "link", "type", "is_active"]
        missingParams = gm.missingParams(requiredParams, data)
        if missingParams:
            missingParams = ", ".join(missingParams)
            return gm.clientError(missingParamMessage.format(missingParams))

        emptyParams = gm.emptyParams(requiredParams, data)
        if emptyParams:
            emptyParams = ", ".join(emptyParams)
            return gm.clientError(emptyParamMessage.format(emptyParams))

        training = Training()
        training.title = str(data["title"]).title()
        training.link = data["link"]
        training.type = data["type"]
        training.is_active = data["is_active"]

        try:
            training.save()
            data = {
                "id" : training.id,
                "title" : training.title,
                "link" : training.link,
                "type" : training.type,
                "is_active" : training.is_active,
                "created_date" : training.created_date
            }
            return gm.successResponse(data)

        except:
            traceback.print_exc()
            gm.log(traceback.format_exc())
            return gm.errorResponse("Error while saving training data.")



