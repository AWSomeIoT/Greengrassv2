import json
import time
import awsiot.greengrasscoreipc
import awsiot.greengrasscoreipc.client as client
from awsiot.greengrasscoreipc.model import GetThingShadowRequest
from awsiot.greengrasscoreipc.model import UpdateThingShadowRequest
import RPi.GPIO as GPIO

#Setup the LED GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(18,GPIO.OUT)

#timeout for messages
TIMEOUT = 10

#initial settings for the reported states of the device
currentstate = json.loads('''{"state": {"reported": {"status": "startup","redledon": false}}}''')

#Get the shadow from the local IPC
def sample_get_thing_shadow_request(thingName, shadowName):
    try:
        # set up IPC client to connect to the IPC server
        ipc_client = awsiot.greengrasscoreipc.connect()
                
        # create the GetThingShadow request
        get_thing_shadow_request = GetThingShadowRequest()
        get_thing_shadow_request.thing_name = thingName
        get_thing_shadow_request.shadow_name = shadowName
        
        # retrieve the GetThingShadow response after sending the request to the IPC server
        op = ipc_client.new_get_thing_shadow()
        op.activate(get_thing_shadow_request)
        fut = op.get_response()
        
        result = fut.result(TIMEOUT)

        #convert string to json object
        jsonmsg = json.loads(result.payload)

        #print desired states
        print(jsonmsg['state']['desired'])    
        
        #if redledon is equal to true/1 then turn on else off
        if jsonmsg['state']['desired']['redledon']:
           print("true turn led on")
           GPIO.output(18,GPIO.HIGH)
        else:
           print("false turn off")
           GPIO.output(18,GPIO.LOW)

        return result.payload
        
    except Exception as e:
        print("Error get shadow", type(e), e)
        # except ResourceNotFoundError | UnauthorizedError | ServiceError


#Set the local shadow using the IPC
def sample_update_thing_shadow_request(thingName, shadowName, payload):
    try:
        # set up IPC client to connect to the IPC server
        ipc_client = awsiot.greengrasscoreipc.connect()
                
        # create the UpdateThingShadow request
        update_thing_shadow_request = UpdateThingShadowRequest()
        update_thing_shadow_request.thing_name = thingName
        update_thing_shadow_request.shadow_name = shadowName
        update_thing_shadow_request.payload = payload
                        
        # retrieve the UpdateThingShadow response after sending the request to the IPC server
        op = ipc_client.new_update_thing_shadow()
        op.activate(update_thing_shadow_request)
        fut = op.get_response()
        
        result = fut.result(TIMEOUT)
        return result.payload
        
    except Exception as e:
        print("Error update shadow", type(e), e)
        # except ConflictError | UnauthorizedError | ServiceError

while(True):

    print("getting shadow document")
    #check document to see if led states need updating
    sample_get_thing_shadow_request('MyPi', 'myNamedShadow')
    time.sleep(1)

    #set current status to good and update actual value of led output to reported
    print("setting shadow good")
    currentstate['state']['reported']['status'] = "good"
    currentstate['state']['reported']['redledon'] = GPIO.input(18)
    sample_update_thing_shadow_request('MyPi', 'myNamedShadow', bytes(json.dumps(currentstate), "utf-8"))   

    time.sleep(10)

    #set current status to bad and update actual value of led output to reported
    print("setting shadow value bad")
    currentstate['state']['reported']['status'] = "bad"
    currentstate['state']['reported']['redledon'] = GPIO.input(18)
    sample_update_thing_shadow_request('MyPi', 'myNamedShadow', bytes(json.dumps(currentstate), "utf-8"))   

    time.sleep(10)
