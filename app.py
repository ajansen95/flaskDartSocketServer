#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import base64
import logging

import cv2
from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from engineio.payload import Payload

from camera.camera import Camera

app = Flask(__name__)
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)
Payload.max_decode_packets = 500
socketio = SocketIO(app)

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


if __name__ == "__main__":
    try:
        socketio.run(app, host="0.0.0.0", port=8080)
    except KeyboardInterrupt:
        camera.stop()
