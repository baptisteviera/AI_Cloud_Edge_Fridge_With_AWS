import concurrent.futures
import sys
import time
import traceback
import json
import awsiot.greengrasscoreipc
import awsiot.greengrasscoreipc.client as client
from awsiot.greengrasscoreipc.model import (
    IoTCoreMessage,
    QOS,
    PublishToIoTCoreRequest,
    SubscribeToTopicRequest,
    SubscriptionResponseMessage,
    UnauthorizedError
)

publishtopic = "device/temp/data"
subscribetopic = "sensor/temp"

TIMEOUT = 20
qos = QOS.AT_LEAST_ONCE

ipc_client = awsiot.greengrasscoreipc.connect()

temperature_now = 4

def publish_temp(temp: float):
    print('Publish temperature ', temp)
    msg = {"temperature": temp}
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
            message = float(str(event.binary_message.message, "utf-8"))
            print("Received new message: ", message)
            global temperature_now
            temperature_now = message
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
            publish_temp(temperature_now)
            print("Message published ", temperature_now)
            time.sleep(30)
            pass
    except InterruptedError:
        print('Subscribe interrupted.')
except Exception:
    print('Exception occurred when using IPC.', file=sys.stderr)
    traceback.print_exc()
    exit(1)
