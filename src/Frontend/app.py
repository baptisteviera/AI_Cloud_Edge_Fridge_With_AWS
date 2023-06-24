from flask import Flask, render_template
import paho.mqtt.client as mqtt
import ssl
import threading
import ast
from AIRecipe import *

app = Flask(__name__)

# intialisation
temp, max_temp = 0, 25
ingredient = ''
recipe = ''
date = ''
@app.route('/')
def index():
    return render_templat/home/snene/PycharmProjects/MTI840-frontende('index.html', date= date, temp=temp, max_temp=max_temp, ingredient=ingredient, recipe=recipe)

def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))


client = mqtt.Client()
client.on_connect = on_connect
client.tls_set(ca_certs='./mti840-frontend/AmazonRootCA1.pem',
               certfile='./mti840-frontend/79463ac588a3d48b8b07746f94ab5a7bccc39f9b370d2b058ed02b88d6d16b74-certificate.pem.crt',
               keyfile='./mti840-frontend/79463ac588a3d48b8b07746f94ab5a7bccc39f9b370d2b058ed02b88d6d16b74-private.pem.key',
               tls_version=ssl.PROTOCOL_SSLv23)
client.tls_insecure_set(True)
client.connect("AWS API", 8883, 60)  # Taken from REST API endpoint - Use your own.


def subscribe(Dummy):
    def on_message(client, userdata, msg):
        """
            The callback function.
            """
        if msg.topic == "device/temp_cloud/ml":
            global ingredient, recipe
            ingredient = ast.literal_eval(msg.payload.decode())
            threading.Thread(target=recipe_generator, args=(ingredient,), ).start()

        if msg.topic == "device/temp/data":
            global temp
            temp = ast.literal_eval(msg.payload.decode())["temperature"]
        print(f"Received from `{msg.topic}` topic")

        if msg.topic == "device/date_expiry/data":
            global date
            date = ast.literal_eval(msg.payload.decode())["date"]
            print(date)
        print(f"Received from `{msg.topic}` topic")

    def on_subscribe(client, userdata, mid, granted_qos):
        print(f"Subscribed{client._client_id.decode()}")

    client.on_subscribe = on_subscribe
    subscription_list = [("device/temp_cloud/ml",0), ("device/temp/data",0), ("device/date_expiry/data",0)]
    client.subscribe(subscription_list)
    client.on_message = on_message
    client.loop_forever()
def recipe_generator(ingredients: list):
    print(ingredients)
    global recipe
    recipe = ai_generation_recipe([key for key in ingredient])
    print("recipe generated")

threading.Thread(target=subscribe, args=("Create intrusion Thread",),).start()

if __name__ == '__main__':
    app.run()
