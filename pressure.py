import Adafruit_BMP.BMP085 as pressure_sensor

sensor = pressure_sensor.BMP085()

pressure = 'Pressure = {0:0.2f} hPa'.format(sensor.read_pressure()/100)#get hPa

altitude = 'Altitude: {0:0.2f} m'.format(sensor.read_altitude())
print(pressure,altitude)
#print('Pressure = {0:0.2f} Pa'.format(sensor.read_pressure()))
#print('Altitude = {0:0.2f} m'.format(sensor.read_altitude()))