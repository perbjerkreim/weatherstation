from gpiozero import Button
import time
import math


wind_count = 0
wind_interval = 1
ADJUSTMENT = 1.18

def spin():
    global wind_count
    wind_count = wind_count + 1
    #print("spin: " + str(wind_count))

def calculate_speed(time_sec):
    global wind_count
    circumference_cm = (2 * math.pi) * radius_cm
    rotations = wind_count / 2.0
    dist_cm = circumference_cm * rotations
    speed_cmh = dist_cm / time_sec
    speed = speed_cmh * 360000 # 3600*100
    return speed * ADJUSTMENT

def reset_wind():
    global wind_count
    wind_count = 0

wind_speed_sensor = Button(18)
wind_speed_sensor.when_pressed = spin

while True:
    wind_count = 0
    time.sleep(wind_interval)
    print(calculate_speed(wind_interval), "m/s")