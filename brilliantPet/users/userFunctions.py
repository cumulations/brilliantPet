from brilliantPet.generalMethods import generalClass
from django.core.exceptions import *
from .models import User


gm = generalClass()


def isLoggedIn(data):
    cleanedData = gm.cleanData(data)

    requiredParams = ["userid", "login_token"]
    missingParams = gm.missingParams(requiredParams, cleanedData)
    if missingParams:
        raise KeyError("({}) missing.".format(", ".join(missingParams)))

    try:
        pass
    except:
        pass


