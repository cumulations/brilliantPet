from django.http import JsonResponse
import time
import traceback
import hashlib
import random
import string
from brilliantPet import settings
import boto3



aws_access_key_id = settings.aws_access_key_id
aws_secret_access_key = settings.aws_secret_access_key
region_name = settings.region_name


class generalClass:

    def successResponse(self, data):
        response = {
            "status" : "success",
            "result" : data
        }

        return JsonResponse(response)


    def clientError(self, message):

        response = {
            "status" : "error",
            "message" : message
        }

        return JsonResponse(response, status = 401)


    def errorResponse(self, message = "Server Exception"):

        response = {
            "status" : "error",
            "message" : message
        }

        return JsonResponse(response, status = 500)

    # To check for missing parameters
    def missingParams(self, requiredParams, data):
        missing = []
        for param in requiredParams:
            if param not in data:
                missing.append(param)

        if missing:
            return missing

        return None

    def emptyParams(self, requiredParams, data):
        isEmpty = []
        empty = ["", None]
        for param in requiredParams:
            if data[param] in empty:
                isEmpty.append(param)

        if isEmpty:
            return isEmpty

        return None


    def log(self, event):
        t = time.localtime(time.time())
        currentDate = "{}-{}-{}".format(t.tm_year, t.tm_mon, t.tm_mday)
        currentTime = "{}:{}:{}".format(t.tm_hour, t.tm_min, t.tm_sec)
        fileName = "logs/{}.{}".format(currentDate, "log")
        try:
            with open(fileName, "a") as file:
                log = currentTime + "\n" + str(event) + "\n\n"
                file.write(log)

            return True
        except:
            traceback.print_exc()

    def cleanData(self, data):

        cleanedData = {}
        for param in data:
            if type(data[param]) == str:
                cleanedData[param] = data[param].strip()

        return cleanedData


    def hash_sha3_512(self, string):

        if type(string) != bytes:
            string = str(string).encode("utf-8")

        sha3 = hashlib.sha3_512()
        sha3.update(string)
        return sha3.hexdigest()


    def randomStringGenerator(self, ssize = 256):

        punctuation = "!^*()"
        r = ''.join([random.choice(string.ascii_letters + string.digits + punctuation) for n in range(ssize)])
        return r



    def invalidToken(self):

        return self.clientError("Invalid login_token.")



    def not_a_user(self):

        return self.clientError("User not registered. Please register first.")



    def userid_or_password_missing(self):

        return self.clientError("Required params 'userid' and 'email' missing.")

    def getS3resource(self):

        s3 = boto3.resource("s3", aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key,
                       region_name=region_name)
        return s3


    def login_details_absent(self, params):

        requiredParams = ["userid", "email"]
        missingParams = self.missingParams(requiredParams, params)
        if missingParams and len(missingParams) > 1:
            return self.userid_or_password_missing()

        requiredParams = ["login_token"]
        missingParams = self.missingParams(requiredParams, params)
        if missingParams:
            return self.clientError("Required param 'login_token' missing.")

        return None












