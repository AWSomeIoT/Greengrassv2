import json
import traceback
import RPi.GPIO as GPIO
import traceback

import awsiot.greengrasscoreipc
import awsiot.greengrasscoreipc.client as client
from awsiot.greengrasscoreipc.model import (
    SubscribeToTopicRequest,
    SubscriptionResponseMessage
)

#Setup the LED GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(18,GPIO.OUT)

#This topic is triggered every time the shadow is updated.
subscribetopic = "$aws/things/MyPi/shadow/name/myNamedShadow/update/accepted"

ipc_client = awsiot.greengrasscoreipc.connect()

TIMEOUT = 10

#Handler for subscription callback
class SubHandler(client.SubscribeToTopicStreamHandler):
    def __init__(self):
        super().__init__()

    def on_stream_event(self, event: SubscriptionResponseMessage) -> None:
        try:
            message_string = str(event.binary_message.message, "utf-8")
            # Load message and check values
            jsonmsg = json.loads(message_string)

            if jsonmsg['state']['desired']['redledon']:
                print("true turn led on")
                GPIO.output(18,GPIO.HIGH)
            else:
                print("false turn off")
                GPIO.output(18,GPIO.LOW)
        except:
            traceback.print_exc()

    def on_stream_error(self, error: Exception) -> bool:
        # Handle error.
        return True  # Return True to close stream, False to keep stream open.

    def on_stream_closed(self) -> None:
        # Handle close.
        pass

#subscribe to topic
request = SubscribeToTopicRequest()
request.topic = subscribetopic 
handler = SubHandler()
operation = ipc_client.new_subscribe_to_topic(handler) 
future = operation.activate(request)
future.result(TIMEOUT)

# Keep the main thread alive, or the process will exit.
while True:
    #time.sleep(10)
    pass


