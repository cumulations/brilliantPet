import paho.mqtt.client as mqtt
import sys
import pymysql
import traceback
import json
from datetime import datetime
from pyfcm import FCMNotification

# sysPath = "../"
sysPath = "/home/ubuntu/brilliantPet/brilliantPet/brilliantPet/mqtt-client/../"
# sys.path.append("/home/ubuntu/brilliantPet/brilliantPet/brilliantPet/mqtt-client/../")
sys.path.append(sysPath)

from brilliantPet.generalMethods import generalClass
p = "/home/ubuntu/brilliantPet/brilliantPet/brilliantPet/mqtt-client/logs"

# p = "./logs"


gm = generalClass()
api_key = "AAAAJAR2tx8:APA91bHRrdbSWalshyjRL-x64k6ckT8zhFG93pXG6h49k5gFnRzoHUzn7W2HuwLTJB2pbfVcSNQx3OzCxDyhn9ZUONBs2SwiFbIvXYzjPFDvohgDgLSxdjv-UH-3hHx8BCNsMqgd-cQQ"


def fcmPush(registration_id, message_title, data_message = None, message_body = "This is a test notification."):

    push_service = FCMNotification(api_key=api_key)
    result = push_service.notify_single_device(registration_id=registration_id, message_title=message_title,
                                               data_message=data_message, message_body = message_body)
    if result["success"] > 0:
        gm.log("Token : {}\nResult : {}\nSuccessful".format(registration_id, result), p)
        print("this is the payload pushed : ", data_message)
        print("FCM push successful")
        return True

    else:
        gm.log("Token : {}\nResult : {}\nFailed".format(registration_id, result), p)
        print(result)
        print("FCM push failed.")
        return False



# def executeSql(sql, con):





def on_connect(client, userdata, flags, rc):

    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.

    mqttTopics = [("/bp/+/event", 0), ("$aws/events/presence/disconnected/+", 0), ("$aws/events/presence/connected/+", 0)]
    client.subscribe(mqttTopics)

    # client.subscribe(("/bp/+/event"), ("aws/events/presence/disconnected/+"))

    log = """
    MQTT client connected. \n
    Flags : {},\n
    userdata : {} \n
    resultCode : {}
    """
    log = log.format(flags, userdata, rc)
    gm.log(log, p)


# def storeDeviceInfo(message):
#
#     value = message["value"]["mark_count"]
#     framesize = message['value']['camera']["framesize"]
#     quality = message["value"]['camera']["quality"]
#
#     sql = ""



# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):

    # print(msg.topic+" "+str(msg.payload))
    print(msg.topic)
    topic = msg.topic.split("/")
    conStatus = topic[-2].lower() in ["connected", "disconnected"]
    device = topic[-1] if conStatus else topic[-2]
    print(device)
    impEvents = ["PAD_ADVANCE_ACK","PAD_ADVANCE", "LOOKIN", "ANIMAL_DETECTION", "DEVICE_ERROR","conStatus"]
    mes = msg.payload.decode('utf-8')
    mes = mes.replace("\n", "")
    payload = json.loads(mes)
    eventType = "conStatus" if conStatus else str(payload["type"])
    if eventType not in impEvents:
        log = "{}\n{}\nmessage received but not saved.".format(msg.topic, msg.payload)
        print(log)
        gm.log(log, p)
        return


    try:
        con = pymysql.connect("localhost", "ubuntu", "password", "brilliantPet")
    except Exception as e:
        traceback.print_exc()
        gm.log(traceback.format_exc(), p)
        con.close()
        return
    else:

        try:
            cursor = con.cursor()

            #checking if the machine and user exists or not

            sql = "select userid, machine_id, name  from users_machinedetails where machine_id like '{}' and isremoved = 0;".format(device)
            cursor.execute(sql)
            query = cursor.fetchall()

            if not query:
                gm.log("{}\n{}\n{}".format(msg.topic, msg.payload, "Device didn't exist."), p)
                print("device didn't exist")
                return


            # if eventType == "DEVICE_INFO":
            #     storeDeviceInfo(msg)

            sql = "select userid from users_user where userid like '{}' and isDeleted = 0;".format(query[0][0])
            cursor.execute(sql)
            query1 = cursor.fetchall()

            if not query1:
                gm.log("{}\n{}\n{}".format(msg.topic, msg.payload, "User doesn't exist or is deleted."), p)
                print("user doesn't exit or is deleted.")
                return

            if conStatus:
                status = 0 if topic[-2].lower() == "disconnected" else 1
                sql = "update users_machinedetails set status = {} where machine_id like '{}';".format(status, device)
                cursor.execute(sql)
                con.commit()
                gm.log("{}\n{}\nStatus updated successfully to {} for device {}.".format(msg.topic, msg.payload, status, device), p)
                print("Status updated successfully.")
                return



            #saving the payload to the db after validated
            print("message received : ", payload)
            sql = "insert into users_events (type, value, machine_id_id, userid_id, date, isflagged, tags, note, tags_value) values ('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}')"
            sql = sql.format(eventType, json.dumps(payload), query[0][1], query[0][0], datetime.now(), 0, '', '', 1)
            cursor.execute(sql)
            con.commit()
            gm.log("{}\n{}\nmessage successfully saved.".format(msg.topic, msg.payload), p)
            print("message successfully saved.")

            #sending notification to the user

            sql = "select token from users_notification_token where userid_id like '{}';".format(query[0][0])
            cursor.execute(sql)
            query3 = cursor.fetchall()
            message = eventType
            title = "{} - Event".format(query[0][2])
            data_message = {
                "device_id" : device,
                "device_name" : query[0][2],
                "payload" : payload
            }
            print(query3)
            for tokens in query3:
                print("token : ", tokens[0])
                fcmPush(tokens[0], title, data_message, message)





        except Exception as e:

            traceback.print_exc()
            gm.log(traceback.format_exc(), p)
            con.rollback()

    finally:
        con.close()






client = mqtt.Client()

path = p + "/../"

# broker = "adovb3uhix8c3-ats.iot.us-east-1.amazonaws.com"
# certPath = path + "4938e6aee5-certificate.pem.crt"
# caPath = path + "ca_certificate.pem"
# keyFile = path + "4938e6aee5-private.pem.key"

broker = "adovb3uhix8c3-ats.iot.us-east-1.amazonaws.com"
certPath = path + "verificationCert.crt"
caPath = path + "AmazonRootCA1.pem"
keyFile = path + "verificationCert.key"

client.on_connect = on_connect
client.on_message = on_message

client.tls_set(caPath, certfile = certPath,  keyfile = keyFile)
print("trying to connect.")
client.connect(broker, 8883)
print("connected")

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
client.loop_forever()
