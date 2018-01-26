from gpiozero import DigitalInputDevice
from time import sleep

rain_sensor = DigitalInputDevice(27) #read from BCM pin 27 (12)
BUCKET_SIZE = 0.2794 #mm of rain needed to tip the bucket
rain_count = 0 #stores the number of tips


def rain():
    global rain_count
    mm_rain = round(rain_count*BUCKET_SIZE,4) #get the total amount of precipitation
    #print("Precipitation: ",mm_rain, "mm")
    return mm_rain

def bucket_tipped():
    global rain_count
    rain_count=rain_count+1

rain_sensor.when_activated = bucket_tipped

while True:
    sleep(1)
    message = "Preciptiation is {}".format(rain()) + " mm"
    print(message)


    