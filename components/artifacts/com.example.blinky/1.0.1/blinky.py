import RPi.GPIO as GPIO
import time
import sys

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(17,GPIO.OUT)

sleeptime = float(sys.argv[1])

while(True):
    GPIO.output(17,GPIO.HIGH)
    print("LED ON")
    time.sleep(sleeptime)
    GPIO.output(17,GPIO.LOW)
    print("LED OFF")
    time.sleep(sleeptime)