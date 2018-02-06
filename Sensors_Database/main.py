import picamera
import sqlite3
from datetime import datetime
import pigpio
import DHT22
from time import sleep
from gpiozero import DigitalInputDevice
from time import sleep
import time
import math
import Adafruit_GPIO.SPI as SPI
import Adafruit_MCP3008
import Adafruit_BMP.BMP085 as pressure_sensor

dbname = 'sensorsData.db'
sampleFreq = 5 # time in seconds

# Software SPI config
CLK  = 18
MISO = 23
MOSI = 24
CS   = 25
mcp = Adafruit_MCP3008.MCP3008(clk=CLK, cs=CS, miso=MISO, mosi=MOSI)

#declare wind direction arrays
NORTH=[384,385,386,768,769,770,771]
NORTHEAST=[437,438,439,440,441,76,77,78]
EAST=[85,86,60,61]
SOUTHEAST=[170,171,172,173,116,117]
SOUTH=[269,270,271,227,228,229]
SOUTHWEST=[606,607,608,609,575,576,577,578]
WEST=[937,938,939,940,941,812,813,814,815]
NORTHWEST=[875,876,877,878,682,683,684]

#declare rain variables
rain_sensor = DigitalInputDevice(27) #read from BCM pin 27
BUCKET_SIZE = 0.2794 #mm of rain needed to tip the bucket
rain_count = 0 #stores the number of tips


#declare wind variables
wind_count = 0 #variable to store number of half-rotations
radius = 0.09 #radius of the anemometer
interval = 5 #frequency to report, in seconds
INERTIA = 1.18 #inertia of the anemometer
store_speeds = [] # stores the last 4 speeds in an array

#create objects
pi = pigpio.pi()
s = DHT22.sensor(pi,4)
psensor = pressure_sensor.BMP085()

#calculate the wind speed
def calculate_speed(time_sec):
    global wind_count
    global store_speeds
    circumference = (2*math.pi)*radius #calculates the circumference of the anemometer
    rotations = wind_count/2.0
    
    #calculate the distance traveled
    distance = circumference*rotations
    
    #calculate speed form distance and time
    m_per_sec = distance/time_sec
    
    #get the acutal speed when factoring in the inertia of the system, and round to last 3 digits
    speed = round(m_per_sec*INERTIA,3)
    
    #store the speed in the array
    store_speeds.append(speed)
    
    #if the array is longer than 4, discard the oldest entry
    if len(store_speeds) > 4:
        store_speeds = store_speeds[1:]
    
    #print the array
    #print(str(store_speeds))
        
    return speed

#check if the last 20 seconds had any gust readings
def check_for_gusts():
    highest = max(store_speeds)
    lowest = min(store_speeds)
    GUST_ABOVE = 8.22 #gust is defined as wind over 8.22 m/s with a duration of atleast 20 secs
    GUST_RANGE = 4.64 #and diff between highest and lowest speed is higher than 4.64 m/s
    if highest > GUST_ABOVE and highest-lowest > GUST_RANGE:
        return highest
    else:
        return 0

#for every 180* rotation, add 1 to count
def spin():
    global wind_count
    wind_count = wind_count +1
    
    
#get direction
def direction():
    DIR="" #declare as empty string
    #read the value of channel 0 and store it in the variable "test" 
    test=mcp.read_adc(0)
    
    #check if test contains a variable in one of the arrays, if so store it in DIR
    if test in NORTH:
        DIR="N"
    elif test in NORTHEAST:
        DIR="NE"
    elif test in EAST:
        DIR="E"
    elif test in SOUTHEAST:
        DIR="SE"
    elif test in SOUTH:
        DIR="S"
    elif test in SOUTHWEST:
        DIR="SW"
    elif test in WEST:
        DIR="W"
    elif test in NORTHWEST:
        DIR="NW"
    return DIR

#get rain
def rain():
    global rain_count
    mm_rain = round(rain_count*BUCKET_SIZE,4) #get the total amount of precipitation
    return mm_rain

def bucket_tipped():
    global rain_count
    rain_count=rain_count+1
    
#read from BCM pin 17
wind_speed_sensor = DigitalInputDevice(17)

#call the spin module when sensor is activated
wind_speed_sensor.when_activated = spin

#call the rain module when the sensor is activated
rain_sensor.when_activated = bucket_tipped

def getDHTdata():
    s.trigger() #tell the sensor to report reading
    time.sleep(0.1) 
    temp = round(s.temperature(),1) #get the temperature, round to 1 decimal after comma
    hum = round(s.humidity(),1) #get the humidity, round to 1 decimal after comma  
    if hum is not None and temp is not None:
        time.sleep(0.1)
        hum = round(hum,1)
        temp = round(temp,1)
    return temp, hum

def logData(temp,hum,speed,dir,rain,pressure,altitude):
    conn=sqlite3.connect(dbname)
    curs=conn.cursor()
    curs.execute("INSERT INTO DHT_data VALUES(datetime('now'), (?), (?), (?), (?), (?), (?), (?))", (temp, hum))
    conn.commit()
    conn.close()


def main():
    while True:
        #BMP180
        pressure = ' Pressure = {0:0.2f} hPa'.format(psensor.read_pressure()/100)#Pa-->hPa
        altitude = ' Altitude : {0:0.2f} m'.format(psensor.read_altitude())
        
        rain = rain()
        dir = direction()
        #DHT22
        temp,hum = getDHTdata()
        
        #wind
        wind_count=0
        sleep(interval)
        speed = calculate_speed(interval)
        
        logData(temp,hum,speed,dir,rain,pressure,altitude)
        
main()