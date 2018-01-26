import time
import Adafruit_GPIO.SPI as SPI
import Adafruit_MCP3008

# Software SPI configuration:
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

#get direction
def direction():
    DIR=""
    #read the value of channel 1(0)and store it in the variable "test" 
    test=mcp.read_adc(0)
    
    #check if test contains a variable in one of the arrays, if so print the direction
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
    print(test)
    return DIR

# Main program loop
while True:
    message = "The wind is coming from "+direction()
    print(message)
    # Pause for half a second.
    time.sleep(0.5)