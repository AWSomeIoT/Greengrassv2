import time
import RPi.GPIO as GPIO
import awsiot.greengrasscoreipc
from awsiot.greengrasscoreipc.model import (
    PublishToTopicRequest,
    PublishMessage,
    BinaryMessage
)

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(4, GPIO.IN,pull_up_down=GPIO.PUD_UP)

ipc_client = awsiot.greengrasscoreipc.connect()

topic = "mypi/button"
message = "b4pressed"
TIMEOUT = 10

def my_callback(channel):
    print('button pressed')
    request = PublishToTopicRequest()
    request.topic = topic
    publish_message = PublishMessage()
    publish_message.binary_message = BinaryMessage()
    publish_message.binary_message.message = bytes(message, "utf-8")
    request.publish_message = publish_message
    operation = ipc_client.new_publish_to_topic()
    operation.activate(request)
    future = operation.get_response()
    future.result(TIMEOUT)



print("button event detect started")

GPIO.add_event_detect(4, GPIO.RISING, callback=my_callback, bouncetime=200)    

# Keep the main thread alive, or the process will exit.
while True:
    #time.sleep(10)
    pass



print("button event detect finished")