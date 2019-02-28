from flask import Flask, request, render_template, send_from_directory, redirect, url_for
from flask_cors import CORS
import psycopg2
import json
from db import *
import yr

app = Flask(__name__, static_folder="map")
CORS(app)

@app.route("/map") # serve frontend, which is in map dir
def map():
    return send_from_directory('map', 'index.html')

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
    return str(yr.getTemperature(segid))

@app.route("/winddata/<segid>")
def winddata(segid):
    return str(yr.getWind(segid))
