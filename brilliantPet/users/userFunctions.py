from brilliantPet.generalMethods import generalClass
from django.core.exceptions import *
from .models import *
import traceback


gm = generalClass()


def isLoggedIn(data, user):
    cleanedData = gm.cleanData(data)

    requiredParams = ["userid", "login_token"]
    missingParams = gm.missingParams(requiredParams, cleanedData)
    if missingParams:
        raise KeyError("({}) missing.".format(", ".join(missingParams)))

    try:
        pass
    except:
        pass


def isUser(data):

    data = gm.cleanData(data)
    try:
        if "email" in data:
            user = User.objects.filter(email = data["email"], isDeleted = 0)
            return user[0]
        if "userid" in data:
            user = User.objects.filter(userid = data["userid"], isDeleted = 0)
            return user[0]

        else:
            return None

    except:
        traceback.print_exc()
        gm.log(traceback.format_exc())
        return None



def securePassword(password):

        password = str(password) + salt
        password = gm.hash_sha3_512(password)
        return password



def register(data):


    cleanedData = gm.cleanData(data)
    requiredParams = ["userid", "name", "notification_token", "rolls_count_at_home", "password", "email", "address", "profile_image"]

    missingParams = gm.missingParams(requiredParams, cleanedData)
    if missingParams:
        raise ValidationError("({}) missing.".format(", ".join(missingParams)))

    if len(str(cleanedData["password"])) < 6:
        raise ValidationError("Password len too short. Should be more than 6 characters.")

    password = securePassword(cleanedData["password"])
    user = User()

    if data["profile_image"] not in ["", None]:
        profile_image = data["profile_image"]
    else:
        profile_image = defaultProfileImage

    user.userid = cleanedData["userid"]
    user.name = cleanedData["name"]
    user.notification_token = cleanedData["notification_token"]
    user.rolls_count_at_home = cleanedData["rolls_count_at_home"]
    user.password = password
    user.login_token = ""
    user.email = cleanedData["email"]
    user.address = cleanedData["address"]
    user.profile_image = profile_image
    user.isDeleted = 0

    user.save()
    return user


def login(data, user):

    cleanedData = gm.cleanData(data)
    password = securePassword(cleanedData["password"])

    if user.email == cleanedData["email"] or user.userid == cleanedData["userid"]:
        if user.password == password:
            login_token = gm.randomStringGenerator()
            user.login_token = login_token
            user.save()
            return login_token

    return None



def authenticate(data, user):

    cleanedData = gm.cleanData(data)

    if user.login_token == cleanedData["login_token"]:
        return True

    return False



def logout(data, user):
    data = gm.cleanData(data)
    if user.login_token == data["login_token"]:
        user.login_token  = ""
        user.save()
        return True

    else:
        return False











