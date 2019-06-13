from django.shortcuts import render
import json
import traceback
from .models import Training
from django.core.exceptions import *
from rest_framework.views import APIView
from django.db import IntegrityError
from brilliantPet import generalMethods
from brilliantPet import settings
import boto3
import base64
import time


# Create your views here.
gm = generalMethods.generalClass()

class trainingView(APIView):

    def get(self, request):

        trainings = Training.objects.filter(is_active = 1)
        data = []
        for training in trainings:
            item = {
                "title" : training.title,
                "link" : training.link,
                "type" : training.type,
                "id" : training.id
            }
            data.append(item)

        return gm.successResponse(data)


