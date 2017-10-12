import smbus, time

from Adafruit_SHT31 import *
from apscheduler.schedulers.blocking import BlockingScheduler

'''
Read temp, humidity, and movement on a rasp pi and
send that data to AWS IoT and DynamoDB services
'''

ACCEL_ADDRESS = 0x1d
TEMPHUM_ADDRESS = 0x44

def configure_accel():
    '''
    Our MMA8451 takes some configuration. Do that here and
    return our configured bus for sampling
    '''
    # Where our MMA8451 accelerometer lives on our I2C bus
    bus = smbus.SMBus(1)

    # To sense movement, we need to set four registers on our
    # MMA8451 accelerometer
    CTRL_REG1    = 0x2A #Used to switch between standby mode and active mode
    FF_MT_CFG    = 0x15 #Config register for freefall and motion
    FF_MT_SRC    = 0x16 #Holds the value of our detected movement
    FF_MT_THS    = 0x17 #Holds our movement threshold value
    FF_MT_COUNT  = 0x18 #Holds the value of our debounce count
    XYZ_DATA_CFG = 0x0E #Controls our high pass filter

    # Let's hop into standby mode
    bus.write_byte_data(ACCEL_ADDRESS, CTRL_REG1, 24)

    # Set our motion config so that we're sensing on x,y
    bus.write_byte_data(ACCEL_ADDRESS, FF_MT_CFG, 216)

    # Set our threshold for movement
    bus.write_byte_data(ACCEL_ADDRESS, FF_MT_THS, 1)

    # Set our debounce counter to 10ms
    bus.write_byte_data(ACCEL_ADDRESS, FF_MT_COUNT, 10)

    # Disable the high pass filter
    bus.write_byte_data(ACCEL_ADDRESS, XYZ_DATA_CFG, 0)

    # Let's hop back into active mode
    bus.write_byte_data(ACCEL_ADDRESS, CTRL_REG1, 25)

    return bus

accel_bus = configure_accel()
previous_accel_reading = 0
moved_during_interval = False

def get_movement():
    accel_reading = accel_bus.read_byte_data(ACCEL_ADDRESS, FF_MT_SRC)
    if previous_accel_reading != accel_reading:
        moved_during_interval = True
    previous_accel_reading = ret

def send_readings():
    sensor = SHT31(address = TEMPHUM_ADDRESS)
    degrees = sensor.read_temperature()
    humidity = sensor.read_humidity()
    print 'Temp = {0:0.3f} deg C'.format(degrees)
    print 'Humidity = {0:0.2f} %'.format(humidity)
    print 'Moved = %s' % moved_during_interval

    moved_during_interval = False


sched = BlockingScheduler()
sched.add_job(get_movement, 'interval', seconds=1)
sched.add_job(send_readings, 'interval', minutes=1)
sched.start()
