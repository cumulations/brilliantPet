import paho.mqtt.client as mqtt
import pymysql

# The callback for when the client receives a CONNACK response from the server.

def on_connect(client, userdata, flags, rc):

    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("/bp/+/event")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(dir(msg))
    print(msg.topic+" "+str(msg.payload))
    device = msg.topic.split("/")[-2]
    print(device)
    con = pymysql.connect("localhost", "root", "password", "brilliantPet")
    print("connected to database.")
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
