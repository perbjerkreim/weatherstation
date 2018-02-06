import time
import sqlite3
import DHT22
import pigpio
dbname = 'sensorsData.db'
sampleFreq = 1 # time in seconds
pi = pigpio.pi()
s = DHT22.sensor(pi,4)

#get data from sensor
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

#log sensor data in database
def logData(temp,hum):
    conn=sqlite3.connect(dbname)
    curs=conn.cursor()
    curs.execute("INSERT INTO DHT_data VALUES(datetime('now'), (?), (?))", (temp, hum))
    conn.commit()
    conn.close()

#main function
def main():
    while True:
        temp,hum = getDHTdata()
        logData(temp,hum)
        time.sleep(sampleFreq)

#execute program
main()
