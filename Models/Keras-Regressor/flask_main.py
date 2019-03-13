from flask import Flask, request, send_from_directory
from flask_cors import CORS
from Backend.db import *
import Backend.yr as yr
import Backend.model as model
import os
import json

app = Flask(__name__, static_folder="Backend/map")
CORS(app)


@app.route("/map")  # serve frontend, which is in map dir
def map():
    return send_from_directory('Backend/map', 'index.html')


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


@app.route("/latest_preds")
def latest_predictions():
    return model.existing_trips_prediction()


@app.route("/current_models")
def current_models():
    models = []
    batches = os.listdir("saved_models")
    for batch in batches:
        models += [batch + "/" + model_name for model_name in os.listdir("saved_models/" + batch) if
                   os.path.isdir("saved_models/" + batch + "/" + model_name)]
    return json.dumps(models)


@app.route("/load_model")
def load_model():
    batch = str(request.args.get('batch'))
    model_name = str(request.args.get('model_name'))
    path = "saved_models/" + batch + "/" + model_name
    model.load_new_model(path)
    return "Model loaded: " + path
