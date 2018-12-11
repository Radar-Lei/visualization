import os
import requests
import json
from flask import Flask, jsonify, render_template, request, session
from flask_socketio import SocketIO, emit, disconnect
import time
from threading import Lock
import eventlet

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
async_mode = None
socketio = SocketIO(app, async_mode=async_mode)

thread = None
thread_lock = Lock()

with open('C:\\Users\\greatraid\\Desktop\\test.json') as json_file:
    data = json.load(json_file)
    trace_data = list(data["data"])
    vehicle_n = len(trace_data)
    tick_len = len(trace_data[0]['ROAD_LINE'].split(';'))


def newPostion(trace_data, timestamp):
    newposition = []
    # print(timestamp)
    # print(type(timestamp))
    for i in range(len(trace_data)):
        ls = trace_data[i]['ROAD_LINE'].split(';')
        point = ls[timestamp].split(',')
        newposition.append([float(point[0]), float(point[1])])
    return newposition


def background_generator():
    """Example of how to send server generated events to clients."""
    while True:
        for i in range(tick_len):
            socketio.sleep(0.001)
            newposition = []
            for j in range(len(trace_data)):
                ls = trace_data[j]['ROAD_LINE'].split(';')
                point = ls[i].split(',')
                newposition.append([float(point[0]), float(point[1])])
            socketio.emit("sending", {"trace": newposition}, namespace='/test')


@app.route("/")
def index():
    return render_template("index_1.html", async_mode=socketio.async_mode)


@socketio.on('connect', namespace='/test')
def get():
    global thread
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(
                target=background_generator)
