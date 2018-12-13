import os
import requests
import json
from flask import Flask, jsonify, render_template, request, session
from flask_socketio import SocketIO, emit, disconnect
import time
from threading import Lock
import eventlet
import numpy as np
import pandas as pd


app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
async_mode = None
socketio = SocketIO(app, async_mode=async_mode)


desktop = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')

with open(desktop+"\\test.json") as json_file:
    data = json.load(json_file)
    trace_data = np.array(list(data["data"]))
    vehicle_n = len(trace_data)
    tick_len = len(trace_data[0]['ROAD_LINE'].split(';'))

tick_applied = 10

n_sections = int(tick_len/tick_applied)


def create_csv(vehicle_n):
    final = []
    for j in range(vehicle_n):
        ls = np.array(trace_data[j]['ROAD_LINE'].split(';'))
        a = np.array_split(ls, n_sections)  # inequally split array return list
        final.append(a)
    return final


#ls = np.array(trace_data[0]['ROAD_LINE'].split(';'))
#b = np.array_split(ls, n_sections)
# print(np.array(b).shape)
# print(ls)

a = np.array(create_csv(vehicle_n))
c = a[:, 0]
print(len(c[0]))

thread = None
thread_lock = Lock()


def background_generator():
    while True:
        for i in range(n_sections):
            socketio.sleep(1)
            points = a[:, i]
            socketio.emit("sending", {"trace": pd.Series(points).to_json(orient='values'), "section_length": len(
                points[0])}, namespace='/test')


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
