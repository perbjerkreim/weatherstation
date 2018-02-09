import time
import sqlite3
import DHT22
import pigpio
from gpiozero import DigitalInputDevice
import Adafruit_GPIO.SPI as SPI
import Adafruit_MCP3008
import Adafruit_BMP.BMP085 as pressure_sensor
import math
import datetime

# Software SPI config
CLK  = 18
MISO = 23
MOSI = 24
CS   = 25
mcp = Adafruit_MCP3008.MCP3008(clk=CLK, cs=CS, miso=MISO, mosi=MOSI)

#DB
dbname = 'sensorsData.db'
sampleFreq = 5 # time in [s]

#temp
pi = pigpio.pi()
s = DHT22.sensor(pi,4)

#Rain
rain_sensor = DigitalInputDevice(27) #read from BCM pin 27 (12)
BUCKET_SIZE = 0.2794 #mm of rain needed to tip the bucket
rain_count = 0 #rain counter

#pressure
psensor = pressure_sensor.BMP085()

#wind
wind_count = 0 #rotation counter
radius = 0.09 #radius of the anemometer, in [m]
interval = 5 #frequency to report, in [s]
COMPENSATION = 1.18 #compensation due to inertia of the anemometer
store_speeds = [] # stores the last 4 speeds in an array

##################################################################################
#Define methods
##################################################################################

#calculate the wind speed
def calculate_speed(time_sec):
    global wind_count
    global store_speeds
    circumference = (2*math.pi)*radius #calculates the circumference of the anemometer
    rotations = wind_count/2.0
    
    #calculate the distance traveled
    distance = (circumference*rotations)
    
    #calculate speed form distance and time
    m_per_sec = distance/time_sec
    
    #get the acutal speed when factoring in the inertia of the system, and round to last 3 digits
    speed = round(m_per_sec*COMPENSATION,3)
    
    #store the speed in the array
    store_speeds.append(speed)
    
    #if the array is longer than 4, discard the oldest entry
    if len(store_speeds) > 4:
        store_speeds = store_speeds[1:]
    
    wind_count = 0
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

#rain
def precipitation():
    global rain_count
    mm_rain = round(rain_count*BUCKET_SIZE,4) #get the total amount of precipitation
    return mm_rain

#for every tip, add 1 to count
def bucket_tipped():
    global rain_count
    rain_count=rain_count+1

#call the tip module when pin is high
rain_sensor.when_activated = bucket_tipped

#read from BCM pin 17
wind_speed_sensor = DigitalInputDevice(17)

#call the spin module when pin is high
wind_speed_sensor.when_activated = spin

#######################################################################################
##
#######################################################################################

#get data from sensor
def getData():
    s.trigger() #tell the sensor to report reading
    time.sleep(0.1) 
    temp = round(s.temperature(),1) #get the temperature, round to 1 decimal after comma
    hum = round(s.humidity(),1) #get the humidity, round to 1 decimal after comma
    rain = round(precipitation(),4)
    pressure = round(psensor.read_pressure()/100, 2)#Pa-->hPa
    altitude = round(psensor.read_altitude(),1)
    windSpeed = round(calculate_speed(interval),2)
    if hum is not None and temp is not None:
        time.sleep(0.1)
        hum = round(hum,1)
        temp = round(temp,1)
        rain = round(rain,4)
        pressure = round(pressure,2)
        altitude = round(altitude,1)
        windSpeed = round(windSpeed,2)
    return temp, hum, rain, pressure, altitude, windSpeed

#log sensor data in database
def logData(temp,hum,rain,pressure,altitude,windSpeed):
    conn=sqlite3.connect(dbname)
    curs=conn.cursor()
    curs.execute("INSERT INTO sensor_data VALUES(datetime('now'), (?), (?), (?), (?), (?), (?))", (temp, hum, rain, pressure, altitude, windSpeed))
    conn.commit()
    conn.close()

#main function
def main():
    while True:
        start = time.time()
        wind_count = 0
        temp,hum,rain, pressure, altitude, windSpeed = getData()
        logData(temp,hum,rain,pressure,altitude,windSpeed)
        time.sleep(sampleFreq)
        end = time.time()
        elapsed = end-start
        print'Logged at: ',time.strftime("%Y-%m-%d %H:%M:%S"),' loop time: ',round(elapsed,2)

#execute program
main()

