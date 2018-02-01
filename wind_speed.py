
from gpiozero import DigitalInputDevice
from time import sleep
import math

wind_count = 0 #variable to store number of half-rotations
radius = 0.09 #radius of the anemometer
interval = 5 #frequency to report, in seconds
INERTIA = 1.18 #inertia of the anemometer
speed_array= [] # stores the last 4 speeds in an array

#calculate the wind speed
def calculate_speed(time_sec):
    global wind_count
    global speed_array
    circumference = (2*math.pi)*radius #calculates the circumference of the anemometer
    rotations = wind_count/2.0
    
    #calculate the distance traveled
    distance = (circumference*rotations)
    
    #calculate speed form distance and time
    m_per_sec = distance/time_sec
    
    #get the acutal speed when factoring in the inertia of the system, and round to last 3 digits
    speed = round(m_per_sec*INERTIA,3)
    
    #store the speed in the array
    speed_array.append(speed)
    
    #if the array is longer than 4, discard the oldest entry
    if len(speed_array) > 4:
        speed_array = speed_array[1:]
    
    #print the array
    #print(str(speed_array))
    
    return speed

#check if the last 20 seconds had any gust readings
def check_for_gusts():
    highest = max(speed_array)
    lowest = min(speed_array)
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
    print(wind_count)
    
#read from BCM pin 17
wind_speed_sensor = DigitalInputDevice(17)

#call the spin module when sensor is activated
wind_speed_sensor.when_activated = spin

#loop and report at a 5 sec interval
while True:
    wind_count = 0
    sleep(interval)
    print("Wind speed is: ",calculate_speed(interval),"m/s")
    #print("Gust speed "+ str(check_for_gusts())+ "m/s")
