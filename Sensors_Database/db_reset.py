import sqlite3 as lite
import sys

con = lite.connect('sensorsData.db')
with con:
    cur = con.cursor()
    cur.execute("DROP TABLE IF EXISTS sensor_data")
    cur.execute("CREATE TABLE sensor_data(timestamp DATETIME,temp NUMERIC,hum NUMERIC,rain NUMERIC,pressure NUMERIC,altitude NUMERIC,windSpeed NUMERIC)")