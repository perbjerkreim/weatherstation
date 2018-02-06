from flask import Flask, render_template, request, send_file, make_response
import sqlite3
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import io


app=Flask(__name__)
conn=sqlite3.connect('../sensorsData.db', check_same_thread=False)
#sqlite3.connect(":memory:", check_same_thread=False)
curs=conn.cursor()

#get data
def getLastData():
    for row in curs.execute("SELECT * FROM DHT_data ORDER BY timestamp DESC LIMIT 1"):
        time = str(row[0])
        temp = row[1]
        hum = row[2]
    #.close()
    return time, temp, hum

def getHistData(numSamples):
    curs.execute("SELECT * FROM DHT_data ORDER BY timestamp DESC LIMIT "+str(numSamples))
    data = curs.fetchall()
    dates = []
    temps = []
    hums = []
    for row in reversed(data):
        dates.append(row[0])
        temps.append(row[1])
        hums.append(row[2])
    return dates, temps, hums

def maxRowsTable():
    for row in curs.execute("SELECT COUNT(temp) from DHT_data"):
        maxNumberRows=row[0]
    return maxNumberRows

#define and initialize global variables
global numSamples
numSamples = maxRowsTable()
if(numSamples > 101):
    numSamples = 100

#main
@app.route("/")
def index():
    time, temp, hum = getLastData()
    templateData = {
        'time': time,
        'temp': temp,
        'hum': hum,
        'numSamples': numSamples
    }
    return render_template('index.html', **templateData)    
    
    
@app.route('/', methods=['POST'])
def my_form_post():
    global numSamples
    numSamples = int(request.form['numSamples'])
    numMaxSamples = maxRowsTable()
    if(numSamples > numMaxSamples):
        numSamples = (numMaxSamples-1)
    time, temp, hum = getLastData()
    templateData = {
        'time': time,
        'temp': temp,
        'hum': hum,
        'numSamples': numSamples
    }
    return render_template('index.html', **templateData)


@app.route('/plot/temp')
def plot_temp():
    times, temps, hums = getHistData(numSamples)
    ys = temps
    fig = Figure()
    axis = fig.add_subplot(1,1,1)
    axis.set_title("Temperature")
    axis.set_label("Samples")
    axis.grid(True)
    axis.set_ylim([-20,40])
    xs = range(numSamples)
    axis.plot(xs,ys)
    canvas = FigureCanvas(fig)
    output = io.BytesIO()
    canvas.print_png(output)
    response = make_response(output.getvalue())
    response.mimetype = 'image/png'
    return response

@app.route('/plot/hum')
def plot_hum():
    times, temps, hums = getHistData(numSamples)
    ys = hums
    fig = Figure()
    axis = fig.add_subplot(1,1,1)
    axis.set_title("Humidity [%]")
    axis.set_label("Samples")
    axis.grid(True)
    xs = range(numSamples)
    axis.set_ylim([0,100])
    axis.plot(xs,ys)
    canvas = FigureCanvas(fig)
    output = io.BytesIO()
    canvas.print_png(output)
    response = make_response(output.getvalue())
    response.mimetype = 'image/png'
    return response


if __name__=="__main__":
    app.run(debug=True)