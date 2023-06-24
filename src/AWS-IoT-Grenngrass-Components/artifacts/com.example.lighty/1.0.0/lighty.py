import concurrent.futures
import sys
import time
import traceback
import RPi.GPIO as GPIO

import awsiot.greengrasscoreipc
import awsiot.greengrasscoreipc.client as client
from awsiot.greengrasscoreipc.model import (
    SubscribeToTopicRequest,
    SubscriptionResponseMessage,
    UnauthorizedError
)

red = 0xFF00
green = 0x00FF
pins = (11, 12)  # pins is a dict
temp = 25
GPIO.setmode(GPIO.BOARD)  # Numbers GPIOs by physical location
GPIO.setup(pins, GPIO.OUT)  # Set pins' mode is output
GPIO.output(pins, GPIO.LOW)  # Set pins to LOW(0V) to off led

p_R = GPIO.PWM(pins[0], 2000)  # set Frequece to 2KHz
p_G = GPIO.PWM(pins[1], 2000)

p_R.start(0)  # Initial duty Cycle = 0(leds off)
p_G.start(0)
topic = "sensor/temp"
TIMEOUT = 10



def map(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min


def setColor(col):  # For example : col = 0x1122
    R_val = col >> 8
    G_val = col & 0x00FF

    R_val = map(R_val, 0, 255, 0, 100)
    G_val = map(G_val, 0, 255, 0, 100)

    p_R.ChangeDutyCycle(R_val)  # Change duty cycle
    p_G.ChangeDutyCycle(G_val)


def destroy():
    p_R.stop()
    p_G.stop()
    GPIO.output(pins, GPIO.LOW)  # Turn off all leds
    GPIO.cleanup()



class StreamHandler(client.SubscribeToTopicStreamHandler):
    def __init__(self):
        super().__init__()

    def on_stream_event(self, event: SubscriptionResponseMessage) -> None:
        try:
            message = float(str(event.binary_message.message, "utf-8"))
            print("Received new message: ",  message)

            if message is not None:
            	if message > temp:
                	setColor(red)
            	else:
                	setColor(green)
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
    request.topic = topic
    handler = StreamHandler()
    operation = ipc_client.new_subscribe_to_topic(handler)
    future = operation.activate(request)

    try:
        future.result(TIMEOUT)
        print('Successfully subscribed to topic: ' + topic)
    except concurrent.futures.TimeoutError as e:
        print('Timeout occurred while subscribing to topic: ' + topic, file=sys.stderr)
        raise e
    except UnauthorizedError as e:
        print('Unauthorized error while subscribing to topic: ' + topic, file=sys.stderr)
        raise e
    except Exception as e:
        print('Exception while subscribing to topic: ' + topic, file=sys.stderr)
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
    destroy()
    traceback.print_exc()
    exit(1)
