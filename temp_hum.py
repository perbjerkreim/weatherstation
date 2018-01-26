from time import sleep
import pigpio
import DHT22

pi = pigpio.pi()
s = DHT22.sensor(pi,4)


#read temperature
def temp():
    s.trigger() #tell the sensor to report reading
    sleep(0.1) #sleep to avoid stack overflow due to processor's speed
    temp = round(s.temperature(),1) #get the temperature, round to 1 decimal after comma
    return temp

def humidity():
    s.trigger() #tell the sensor to report reading
    sleep(0.1) #sleep to avoid stack overflow due to processors's speed
    humidity = round(s.humidity(),1) #get the humidity, round to 1 decimal after comma
    return humidity

while True:
    sleep(5)
    print('Temperature:',temp(),'*C', 'Humidity: ',humidity(),'%')
    