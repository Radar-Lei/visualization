import os
import requests
import json
from flask import Flask, jsonify, render_template, request
from flask_socketio import SocketIO, emit
import time
import eventlet
eventlet.monkey_patch()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
async_mode = 'eventlet'
socketio = SocketIO(app, async_mode=async_mode)

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


@app.route("/")
def index():
    return render_template("index_1.html")


@socketio.on("request data")
def get():
    for i in range(tick_len):
        print(i)
        emit("sending", {"trace": newPostion(trace_data, i)})
        socketio.sleep(1)
