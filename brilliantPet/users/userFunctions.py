from brilliantPet.generalMethods import generalClass
from django.core.exceptions import *
from .models import *
import traceback


gm = generalClass()

def getUser(data):
    data = gm.cleanData(data)
    try:
        if "email" in data and data["email"] not in ["", None]:
            user = User.objects.filter(email=data["email"], isDeleted=0)
            return user[0]
        if "userid" in data and data["userid"] not in ["", None]:
            user = User.objects.filter(userid=data["userid"], isDeleted=0)
            return user[0]
        else:
            return None
    except:
        traceback.print_exc()
        gm.errorLog(traceback.format_exc())
        return None



isUser = getUser     # just for better naming of functions



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

    flag = 0
    cleanedData = gm.cleanData(data)
    password = securePassword(cleanedData["password"])

    if "email" in cleanedData and user.email == cleanedData["email"]:
        flag = 1

    elif "userid" in cleanedData and user.userid == cleanedData["userid"]:
        flag = 1

    if flag == 1 and user.password == password:

        login_token = gm.randomStringGenerator()
        user.login_token = login_token
        user.save()
        return login_token

    return None



def authenticate(data):

    data = gm.cleanData(data)

    missingLoginDetails = gm.login_details_absent(data)
    if missingLoginDetails:
        return missingLoginDetails

    user = isUser(data)
    if not user:
        return gm.not_a_user()

    if user.login_token == data["login_token"]:
        return False

    return gm.invalidToken()


def logout(data, user):
    data = gm.cleanData(data)
    if user.login_token == data["login_token"]:
        user.login_token = ""
        user.save()
        return True

    else:
        return False














