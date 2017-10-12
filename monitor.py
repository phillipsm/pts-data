import random, json, logging, argparse
from os import environ

from Adafruit_SHT31 import *
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
from apscheduler.schedulers.blocking import BlockingScheduler

'''
Read temp, humidity, and create fake movement data on a
rasp pi and send that data to AWS IoT and DynamoDB services
'''

# I2C Address of our temp and hum device
TEMPHUM_ADDRESS = 0x44

# Credentials and settings for AWS IoT
IOT_HOST = environ['IOT_HOST']
ROOT_CA_PATH = environ['ROOT_CA_PATH']
CERT_PATH = environ['CERT_PATH']
PRIVATE_KEY_PATH = environ['PRIVATE_KEY_PATH']
CLIENT_ID = environ['CLIENT_ID']
TOPIC = environ['TOPIC']
DEVICE_ID = environ['DEVICE_ID']

def send_readings():
    sensor = SHT31(address = TEMPHUM_ADDRESS)
    temp = sensor.read_temperature()
    humidity = sensor.read_humidity()

    payload = {'device_id': DEVICE_ID,
        'activity': random.choice([True, False]),
        'humidity': humidity, 'temp': temp}

    # Configure aws iot
    # General message notification callback
    def customOnMessage(message):
        print("Received a new message: ")
        print(message.payload)
        print("from topic: ")
        print(message.topic)
        print("--------------\n\n")


    # Suback callback
    def customSubackCallback(mid, data):
        print("Received SUBACK packet id: ")
        print(mid)
        print("Granted QoS: ")
        print(data)
        print("++++++++++++++\n\n")

    logger = logging.getLogger("AWSIoTPythonSDK.core")
    logger.setLevel(logging.DEBUG)
    streamHandler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    streamHandler.setFormatter(formatter)
    logger.addHandler(streamHandler)

    myAWSIoTMQTTClient = AWSIoTMQTTClient(CLIENT_ID)
    myAWSIoTMQTTClient.configureEndpoint(IOT_HOST, 8883)
    myAWSIoTMQTTClient.configureCredentials(ROOT_CA_PATH, PRIVATE_KEY_PATH, CERT_PATH)

    # AWSIoTMQTTClient connection configuration
    myAWSIoTMQTTClient.configureAutoReconnectBackoffTime(1, 32, 20)
    myAWSIoTMQTTClient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
    myAWSIoTMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
    myAWSIoTMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
    myAWSIoTMQTTClient.configureMQTTOperationTimeout(5)  # 5 sec
    myAWSIoTMQTTClient.onMessage = customOnMessage

    # Connect and subscribe to AWS IoT
    myAWSIoTMQTTClient.connect()
    myAWSIoTMQTTClient.subscribeAsync(TOPIC, 1, ackCallback=customSubackCallback)
    myAWSIoTMQTTClient.publishAsync(TOPIC, json.dumps(payload), 1, ackCallback=customSubackCallback)

    print json.dumps(payload)

send_readings()


sched = BlockingScheduler()
sched.add_job(send_readings, 'interval', seconds=15)
sched.start()
