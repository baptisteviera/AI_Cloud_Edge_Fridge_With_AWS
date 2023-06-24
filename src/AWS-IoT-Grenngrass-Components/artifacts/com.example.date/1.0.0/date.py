import concurrent.futures
import sys
import time
import traceback
import json
import awsiot.greengrasscoreipc
import awsiot.greengrasscoreipc.client as client
import requests
import random
import os
from awsiot.greengrasscoreipc.model import (
    IoTCoreMessage,
    QOS,
    PublishToIoTCoreRequest,
    SubscribeToTopicRequest,
    SubscriptionResponseMessage,
    UnauthorizedError
)

publishtopic = "device/date_expiry/data"
subscribetopic = "sensor/button"

TIMEOUT = 20
qos = QOS.AT_LEAST_ONCE

ipc_client = awsiot.greengrasscoreipc.connect()

expiry_date = "no expiry date found"


def read_image_path(folder_path="/home/pi/components/artifacts/com.example.date/1.0.0/data_expiry_date"):
    files = os.listdir(folder_path)

    if len(files) > 0:
        random_number = random.randint(0, len(files)-1)
        print("random_number ", random_number)
        first_file_path = os.path.join(folder_path, files[random_number])
        print("first_file_path ", first_file_path)

    return first_file_path


def publish_date(date_expiry):
    print('Publish expiry date ', date_expiry)
    msg = {"date": date_expiry}
    msgstring = json.dumps(msg)

    pubrequest = PublishToIoTCoreRequest()
    pubrequest.topic_name = publishtopic
    pubrequest.payload = bytes(msgstring, "utf-8")
    pubrequest.qos = qos
    operation = ipc_client.new_publish_to_iot_core()
    operation.activate(pubrequest)
    future = operation.get_response()
    future.result(TIMEOUT)


class StreamHandler(client.SubscribeToTopicStreamHandler):
    def __init__(self):
        super().__init__()

    def on_stream_event(self, event: SubscriptionResponseMessage) -> None:
        try:
            # message = float(str(event.binary_message.message, "utf-8"))
            # print("Received new message: ", message)
            url = 'http://54.243.23.146/date_expiry/'
            my_img_path = read_image_path()
            print(my_img_path)
            my_img = {'image': open(my_img_path, 'rb')}
            r = requests.post(url, files=my_img)
            # convert server response into JSON format.
            print(r.text)
            publish_date(r.text)
            #time.sleep(120)
        except:
            traceback.print_exc()

    def on_stream_error(self, error: Exception) -> bool:
        print("Received a stream error.", file=sys.stderr)
        traceback.print_exc()
        return False  # Return True to close stream, False to keep stream open.

    def on_stream_closed(self) -> None:
        print('Subscribe to topic stream closed.')


try:
    ipc_client = awsiot.greengrasscoreipc.connect()

    request = SubscribeToTopicRequest()
    request.topic = subscribetopic
    handler = StreamHandler()
    operation = ipc_client.new_subscribe_to_topic(handler)
    future = operation.activate(request)

    try:
        future.result(TIMEOUT)
        print('Successfully subscribed to topic: ' + subscribetopic)
    except concurrent.futures.TimeoutError as e:
        print('Timeout occurred while subscribing to topic: ' + subscribetopic, file=sys.stderr)
        raise e
    except UnauthorizedError as e:
        print('Unauthorized error while subscribing to topic: ' + subscribetopic, file=sys.stderr)
        raise e
    except Exception as e:
        print('Exception while subscribing to topic: ' + subscribetopic, file=sys.stderr)
        raise e

    # Keep the main thread alive, or the process will exit.
    try:
        while True:
            pass
    except InterruptedError:
        print('Subscribe interrupted.')
except Exception:
    print('Exception occurred when using IPC.', file=sys.stderr)
    traceback.print_exc()
    exit(1)
