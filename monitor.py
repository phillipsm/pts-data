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

def send_readings():
    sensor = SHT31(address = TEMPHUM_ADDRESS)
    temp = sensor.read_temperature()
    humidity = sensor.read_humidity()

    payload = {'activity': random.choice([True, False]),
        'humidity': humidity, 'temp': temp}

    # Configure logging
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
    myAWSIoTMQTTClient.publishAsync(TOPIC, json.dumps(paysload), 1)

    print json.dumps(payload)

sched = BlockingScheduler()
sched.add_job(send_readings, 'interval', seconds=2)
sched.start()
