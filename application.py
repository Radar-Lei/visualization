import os
import requests
import json
from flask import Flask, jsonify, render_template, request
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
socketio = SocketIO(app)

with open('C:\\Users\\greatraid\\Desktop\\test.json') as json_file:
    data = json.load(json_file)
    trace_data = list(data["data"])
    vehicle_n = len(trace_data)


def newPostion(trace_data, timestamp):
    newposition = []
    print(timestamp)
    print(type(timestamp))
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
    emit("initial", {"trace": newPostion(trace_data, 0),
                     "vehicle_n": vehicle_n}, broadcast=True)


@socketio.on("newPosition")
def newData(data):
    emit("sending", {"trace": newPostion(trace_data, data["timestamp"])})
