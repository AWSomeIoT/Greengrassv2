import time
import traceback
import json
import RPi.GPIO as GPIO
import awsiot.greengrasscoreipc
import awsiot.greengrasscoreipc.client as client
from awsiot.greengrasscoreipc.model import (
    IoTCoreMessage,
    QOS,
    PublishToIoTCoreRequest,
    SubscribeToIoTCoreRequest
)

#Setup the button GPIO
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(4, GPIO.IN,pull_up_down=GPIO.PUD_UP)

#Setup the LED GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(18,GPIO.OUT)



publishtopic = "mypi/button"
subscribetopic = "mypi/mqtt"
message =  {
  "button": "b4pressed",
  "timemillis": 000000000000
}

TIMEOUT = 10
qos = QOS.AT_LEAST_ONCE
subqos = QOS.AT_MOST_ONCE


ipc_client = awsiot.greengrasscoreipc.connect()


#button 4 callback
def button4pressed(channel):
    print('button pressed')

    message["timemillis"] = round(time.time() * 1000)

    msgstring = json.dumps(message)

    pubrequest = PublishToIoTCoreRequest()
    pubrequest.topic_name = publishtopic
    pubrequest.payload = bytes(msgstring, "utf-8")
    pubrequest.qos = qos
    operation = ipc_client.new_publish_to_iot_core()
    operation.activate(pubrequest)
    future = operation.get_response()
    future.result(TIMEOUT)


#print("button event detect started")
#Subscribe to the button state change event
GPIO.add_event_detect(4, GPIO.RISING, callback=button4pressed, bouncetime=200)    


#Code to subscribe to topic from 
class SubHandler(client.SubscribeToIoTCoreStreamHandler):
    def __init__(self):
        super().__init__()

    def on_stream_event(self, event: IoTCoreMessage) -> None:
        try:
            message = str(event.message.payload, "utf-8")
            topic_name = event.message.topic_name
            # Handle message.
            jsonmsg = json.loads(message)

            if jsonmsg["ledon"]:
                print("true turn on")
                GPIO.output(18,GPIO.HIGH)
            else:
                print("turn off")
                GPIO.output(18,GPIO.LOW)

        except:
            traceback.print_exc()

    def on_stream_error(self, error: Exception) -> bool:
        # Handle error.
        return True  # Return True to close stream, False to keep stream open.

    def on_stream_closed(self) -> None:
        # Handle close.
        pass




subrequest = SubscribeToIoTCoreRequest()
subrequest.topic_name = subscribetopic
subrequest.qos = subqos
handler = SubHandler()
operation = ipc_client.new_subscribe_to_iot_core(handler)
future = operation.activate(subrequest)
future.result(TIMEOUT)

# Keep the main thread alive, or the process will exit.
while True:
    #time.sleep(10)
    pass



print("button event detect finished")