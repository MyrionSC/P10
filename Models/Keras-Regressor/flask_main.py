from flask import Flask, request, send_from_directory, Response
from flask_cors import CORS
from Backend.db import *
import Backend.yr as yr
import Backend.model as model
import os
import json
from Utils.Errors import TripNotFoundError


app = Flask(__name__, static_folder="Backend/map")
CORS(app)


#Serve frontend
@app.route("/map")  # serve frontend, which is in map dir
def map():
    return send_from_directory('Backend/map', 'index.html')


# api
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


@app.route("/predict")
def predict():
    trip = int(request.args.get('trip'))
    try:
        res = model.trip_prediction(trip)
    except TripNotFoundError as e:
        return Response(str(e), status=404)
    return res


@app.route("/current_models")
def current_models():
    response = {
        'current_model': model.current_model,
        'available_models': []
    }

    batches = os.listdir("saved_models")
    for batch in batches:
        response['available_models'] += [batch + "/" + model_name for model_name in os.listdir("saved_models/" + batch) if
                   os.path.isdir("saved_models/" + batch + "/" + model_name)]
    return json.dumps(response)


@app.route("/load_model")
def load_model():
    batch = str(request.args.get('batch'))
    model_name = str(request.args.get('model_name'))
    path = "saved_models/" + batch + "/" + model_name
    model.load_new_model(path)
    model.current_model = path
    return json.dumps("Model loaded: " + path)


@app.route("/predict_segs", methods=['GET', 'POST'])
def predict_segs():
    body = request.get_json()
    segs = body['segments']
    directions = body['directions']
    return model.do_segment_predictions(segs, directions)
