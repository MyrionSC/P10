from flask import Flask, request, render_template
from flask_cors import CORS
import psycopg2
import json
app = Flask(__name__)
CORS(app)

database = {
    "name": "ev_smartmi",
    "user": "smartmi",
    "port": "4102",
    "host": "172.19.1.104",
    "password": "63p467R=530"
}

def query(str):
    conn = psycopg2.connect("dbname='{0}' user='{1}' port='{2}' host='{3}' password='{4}'".format(database['name'], database['user'], database['port'], database['host'], database['password']))
    cur = conn.cursor()
    cur.execute(str)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

@app.route("/")
def hello():
    return "Maybe serve client from this endpoint"

@app.route("/map")
def route():
    origin = int(request.args.get('origin'))
    dest = int(request.args.get('dest'))
    geojson = get_route(origin, dest)
    return render_template('test.html', geojson=geojson)
    

@app.route("/route")
def get_json():
    origin = int(request.args.get('origin'))
    dest = int(request.args.get('dest'))
    return get_route(origin, dest)


def get_route(origin, dest):
    qry = """
    SELECT row_to_json(fc)::text as path
        FROM(
            SELECT
                'FeaturesCollection' as "type",
                array_to_json(array_agg(f)) as "features"
            FROM (
                SELECT
                    'Feature' as "type",
                    ST_AsGeoJSON(segmentgeo, 6) :: json as "geometry"
                FROM (
                    SELECT
                        osm_dk_20140101.segmentgeo
                    FROM pgr_dijkstra('SELECT edg.*, meters as cost FROM experiments.rmp10_edges edg JOIN maps.osm_dk_20140101 osm ON osm.segmentkey = edg.segmentkey'::text, {0}::bigint, {1}::bigint) pgr
                    JOIN maps.osm_dk_20140101 ON pgr.edge = osm_dk_20140101.segmentkey
                ) as q
            ) as f
        ) as fc
    """.format(origin, dest)
    return query(qry)[0][0]

@app.route("/test_route")
def test():
    return render_template('test.html')
