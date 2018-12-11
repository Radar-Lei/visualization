import os
import requests
import json
from flask import Flask, jsonify, render_template, request, url_for, copy_current_request_context
from flask_socketio import SocketIO, emit
from time import sleep
from threading import Thread, Event

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")


with open('C:\\Users\\greatraid\\Desktop\\test.json') as json_file:
    data = json.load(json_file)
    trace_data = list(data["data"])
    vehicle_n = len(trace_data)
    tick_len = len(trace_data[0]['ROAD_LINE'].split(';'))

# turn the flask app into a socketio app
socketio = SocketIO(app)

# random number Generator Thread
thread = Thread()
thread_stop_event = Event()


class RandomThread(Thread):
    def __init__(self):
        self.delay = 1
        super(RandomThread, self).__init__()

    def randomNumberGenerator(self):
        """
        Generate a random number every 1 second and emit to a socketio instance (broadcast)
        Ideally to be run in a separate thread?
        """
        # infinite loop of magical random numbers
        print("Making random numbers")
        for i in range(tick_len):
            print(i)
            emit("sending", {"trace": newPostion(trace_data, i)})
            socketio.sleep(1)

        """
        while not thread_stop_event.isSet():
            number = round(random()*10, 3)
            print(number)
            socketio.emit('newnumber', {'number': number}, namespace='/test')
            sleep(self.delay)
"""

    def run(self):
        self.randomNumberGenerator()


@app.route('/')
def index():
    # only by sending this page first will the client be connected to the socketio instance
    return render_template('index.html')


@socketio.on('connect', namespace='/test')
def test_connect():
    # need visibility of the global thread object
    global thread
    print('Client connected')

    # Start the random number generator thread only if the thread has not been started before.
    if not thread.isAlive():
        print("Starting Thread")
        thread = RandomThread()
        thread.start()


@socketio.on('disconnect', namespace='/test')
def test_disconnect():
    print('Client disconnected')


if __name__ == '__main__':
    socketio.run(app)


def newPostion(trace_data, timestamp):
    newposition = []
    # print(timestamp)
    # print(type(timestamp))
    for i in range(len(trace_data)):
        ls = trace_data[i]['ROAD_LINE'].split(';')
        point = ls[timestamp].split(',')
        newposition.append([float(point[0]), float(point[1])])
    return newposition


thread = None


@app.route("/")
def index():
    return render_template("index_1.html")


@socketio.on("request data")
def get():
    global thread
    if thread is None:
        thread = socketio.start_background_task(target=background_sending)
