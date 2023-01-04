#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import base64
import logging
from random import randint
import time

import cv2
from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from engineio.payload import Payload

from camera.camera import Camera
from camera.manipulation import get_current_point

app = Flask(__name__)
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)
Payload.max_decode_packets = 500
socketio = SocketIO(app, cors_allowed_origins='*')

camera = Camera()
camera.start()


@app.route("/video")
def video():
    """Video streaming home page."""
    return render_template("video.html")


@socketio.on("request-frame", namespace="/camera-feed")
def camera_frame_requested(message):
    frame = camera.get_frame()
    if frame is not None:
        emit("new-frame", {
            "base64": base64.b64encode(frame).decode("ascii")
        })


@app.route("/manipulated_video")
def manipulated_video():
    """Video streaming home page."""
    return render_template("manipulated_video.html")


@socketio.on("request-manipulated-frame", namespace="/manipulated-camera-feed")
def camera_frame_requested(message):
    frame = camera.get_manipulated_frame()
    if frame is not None:
        emit("manipulated-new-frame", {
            "base64": base64.b64encode(frame).decode("ascii")
        })


@app.route("/points_socket")
def points_feed():
    """Points streaming home page."""
    return render_template("points_socket.html")


@socketio.on("request-current-point", namespace="/current-point-feed")
def current_points(message):
    while True:
        point = get_current_point()
        if point is not None:
            multiplier = str(point[0])
            points = str(point[1])
            # print(str_point)
            emit("current-point", {
                "multipier": multiplier,
                "points": points
            })
        else:
            multiplier = str(randint(1, 3))
            points = str(randint(1, 20))
            string = multiplier + " * " + points
            print(string)
            emit("current-point", {
                "multipier": multiplier,
                "points": points
            })
        time.sleep(3)




if __name__ == "__main__":
    try:
        socketio.run(app, host="0.0.0.0", port=8080)
    except KeyboardInterrupt:
        camera.stop()
