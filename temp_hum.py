from time import sleep
import pigpio
import DHT22

pi = pigpio.pi()
s = DHT22.sensor(pi,4)


#read temperature
def temp():
    s.trigger() #tell the sensor to report reading
    sleep(0.1) #
    temp = round(s.temperature(),1) #get the temperature, round to 1 decimal after comma
    return temp

def humidity():
    s.trigger() #tell the sensor to report reading
    sleep(0.1) 
    humidity = round(s.humidity(),1) #get the humidity, round to 1 decimal after comma
    return humidity

while True:
    sleep(5)
    print('Temperature:',temp(),'*C', 'Humidity: ',humidity(),'%')
    
