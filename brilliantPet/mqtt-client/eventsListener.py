import paho.mqtt.client as mqtt
import sys
import pymysql
import traceback
import json
from datetime import datetime

sys.path.append("../")

from brilliantPet.generalMethods import generalClass

#for saving events for devices


# The callback for when the client receives a CONNACK response from the server.
gm = generalClass()


def on_connect(client, userdata, flags, rc):

    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("/bp/+/event")

    log = """
    MQTT client connected. \n
    Flags : {},\n
    userdata : {} \n,
    resultCode : {}
    """
    log = log.format(flags, userdata, rc)
    gm.log(log)

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):

    # print(msg.topic+" "+str(msg.payload))
    device = msg.topic.split("/")[-2]
    print(device)
    try:
        con = pymysql.connect("localhost", "ubuntu", "password", "brilliantPet")
    except Exception as e:
        traceback.print_exc()
        gm.log(traceback.format_exc())
        con.close()
        return
    else:

        try:
            cursor = con.cursor()
            sql = "select userid, machine_id  from users_machinedetails where machine_id like '{}' and isremoved = 0;".format(device)
            cursor.execute(sql)
            query = cursor.fetchall()

            if not query:
                gm.log("{}\n{}\n{}".format(msg.topic, msg.payload, "device doesn't exist"))
                print("device didn't exist")
                return


            mes = msg.payload.decode('utf-8')
            mes = mes.replace("\n", "")
            message = json.loads(mes)
            eventType = str(message["type"])
            print("message received : ", message)
            sql = "insert into users_events (type, value, machine_id_id, userid_id, date) values ('{}', '{}', '{}', '{}', '{}')"
            sql = sql.format(eventType, json.dumps(message), query[0][1], query[0][0], datetime.now())
            cursor.execute(sql)
            con.commit()
            gm.log("{}\n{}\n{}".format(msg.topic, msg.payload, "saved successfully"))
            print("message successfully saved.")



        except Exception as e:

            traceback.print_exc()
            gm.log(traceback.format_exc())
            con.rollback()

    finally:
        con.close()






client = mqtt.Client()

path = "./"

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
