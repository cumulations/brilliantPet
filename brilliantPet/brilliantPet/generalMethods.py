from django.http import JsonResponse
import time
import traceback
import hashlib
import random
import string
from brilliantPet import settings
import boto3
import os



aws_access_key_id = settings.aws_access_key_id
aws_secret_access_key = settings.aws_secret_access_key
region_name = settings.region_name

missingParamMessage = "({}) missing in post data."
emptyParamMessage = "({}) empty in post data."
loginBasic = ["userid", "password", "email"]
authenticationBasic = ["userid", "email", "login_token"]
notUserMessage = "User not registered. Please register first."
getNotSupported = "GET Method not supported."


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
            try:
                if data[param] in empty:
                    isEmpty.append(param)
            except:
                pass

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

            if param == "email":
                cleanedData[param] = data[param].lower()

        return cleanedData


    def hash_sha3_512(self, string):

        if type(string) != bytes:
            string = str(string).encode("utf-8")

        sha3 = hashlib.sha3_512()
        sha3.update(string)
        return sha3.hexdigest()


    def randomStringGenerator(self, ssize = 4):

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


    def generate_url(self, fileName, bucketName):
        baseUrl = "https://s3.{}.amazonaws.com/{}/{}"
        return baseUrl.format(region_name, bucketName, fileName)


    def uploadToS3(self, bucketName, fileName, file, ContentType = "image/jpeg", ACL = 'public-read'):

        try:
            s3 = self.getS3resource()
            folder = s3.Bucket(bucketName)
            i = folder.put_object(Key=fileName, Body=file, ACL=ACL, ContentType=ContentType)
            download_url = self.generate_url(fileName, bucketName)

            return download_url

        except:
            traceback.print_exc()
            self.log(traceback.format_exc())
            return None


    def getFileExtension(self, fileName):

        fileName = str(fileName).strip()
        name, ext = os.path.splitext(fileName)
        return ext

    def getUniqueFileName(self, ext = ""):

        ct = int(time.time() * 10000)
        randomString = self.randomStringGenerator(6)
        fileName = "{}{}{}".format(randomString, ct, ext)

        return fileName


    def change(self, object, data, changeableList):

        for item in changeableList:
            if item in data:
                setattr(object, item, data[item])

        object.save()
        return object













