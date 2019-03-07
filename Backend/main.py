from flask import Flask, request, send_from_directory
from flask_cors import CORS
from db import *
import yr

app = Flask(__name__, static_folder="map")
CORS(app)


@app.route("/map")  # serve frontend, which is in map dir
def map():
    return send_from_directory('map', 'index.html')


@app.route("/baseline")
def baseline():
    origin = int(request.args.get('origin'))
    dest = int(request.args.get('dest'))
    return get_baseline(origin, dest)


@app.route("/route")
def get_json():
    origin = int(request.args.get('origin'))
    dest = int(request.args.get('dest'))
    return get_route(origin, dest)


@app.route("/embedding")
def emb():
    key = int(request.args.get('key'))
    return get_embedding(key)


@app.route("/temperature/<segid>")
def temperature(segid):
    return str(yr.get_temperature(segid))


@app.route("/winddata/<segid>")
def winddata(segid):
    return str(yr.get_wind(segid))
