import concurrent.futures
import sys
import time
import traceback
import json
import os
import awsiot.greengrasscoreipc
import awsiot.greengrasscoreipc.client as client
import RoboflowModel
import random
from awsiot.greengrasscoreipc.model import (
    # publish the result of the modele ML
    PublishToTopicRequest,
    PublishMessage,
    BinaryMessage,

    # suscribe to the topic button
    SubscribeToTopicRequest,
    SubscriptionResponseMessage,
    UnauthorizedError
)

publishtopic = "device/temp/ml"
subscribetopic = "sensor/button"

TIMEOUT = 30
# qos = QOS.AT_LEAST_ONCE

ipc_client = awsiot.greengrasscoreipc.connect()

# temperature_now = 4

items_message = ""




def modelai(image_path):
    return RoboflowModel.count_object_occurances(RoboflowModel.all_targets,image_path)
    # return  RoboflowModel.items_type_in_fridge_str(image_path) jhghg
    
def read_image_path(folder_path="/home/pi/components/artifacts/com.example.image_items/1.0.0/data_fridge_content"):
    files = os.listdir(folder_path)

    if len(files) > 0:
        random_number = random.randint(0, len(files)-1)
        print("random_number ", random_number)
        first_file_path = os.path.join(folder_path, files[random_number])
        print("first_file_path ", first_file_path)

    return first_file_path

def publish(message):
    # print('button pressed')
    request = PublishToTopicRequest()
    request.topic = publishtopic
    publish_message = PublishMessage()
    publish_message.binary_message = BinaryMessage()
    publish_message.binary_message.message = bytes(str(message), "utf-8")
    print(str(publish_message.binary_message.message, "utf-8"))
    request.publish_message = publish_message
    operation = ipc_client.new_publish_to_topic()
    operation.activate(request)
    future = operation.get_response()
    future.result(TIMEOUT)


class StreamHandler(client.SubscribeToTopicStreamHandler):
    def __init__(self):
        super().__init__()

    def on_stream_event(self, event: SubscriptionResponseMessage) -> None:
        try:
            # message = str(event.binary_message.message, "utf-8")
            # print("Received new message: ", message)
            # global bouton_status
            # bouton_status = message
            image_path = read_image_path()
            print("image_path ", image_path)
            items_message = RoboflowModel.count_object_occurances(target_class = RoboflowModel.all_targets,img_file = image_path)
            print("Message published ", items_message)
            publish(items_message)

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
            # time.sleep(10)
            pass
    except InterruptedError:
        print('Subscribe interrupted.')

except Exception:
    print('Exception occurred when using IPC.', file=sys.stderr)
    traceback.print_exc()
    exit(1)


