import random, json

from Adafruit_SHT31 import *
from apscheduler.schedulers.blocking import BlockingScheduler

'''
Read temp, humidity, and create fake movement data on a
rasp pi and send that data to AWS IoT and DynamoDB services
'''

TEMPHUM_ADDRESS = 0x44

def send_readings():
    sensor = SHT31(address = TEMPHUM_ADDRESS)
    temp = sensor.read_temperature()
    humidity = sensor.read_humidity()
    
    payload = {'activity': random.choice([True, False]),
        'humidity': humidity, 'temp': temp}

    print json.dumps(payload)

sched = BlockingScheduler()
sched.add_job(send_readings, 'interval', seconds=1)
sched.start()
