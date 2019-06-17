import sys
import psycopg2
from psycopg2.extras import RealDictCursor
import os

path = "../Frontend/src/assets/"


def query(str):
    conn = psycopg2.connect("dbname='ev_smartmi' user='smartmi' port='4102' host='172.19.1.104' password='63p467R=530'")
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute(str)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


tl = {'ss': 'supersegment',
      's': 'segment',
      's_emb': 'segment-emb',
      'base': 'baseline'}


def get_qry(trip_id):
    return """
    WITH trip_ss AS (
        SELECT *
        FROM experiments.rmp10_all_trip_data
        WHERE trip_id = {0}
        ORDER BY start_segmentno
    ), trip_vals_ss AS (
        SELECT 
            trip.superseg_id,
            trip.start_segmentno,
            trip.ev_wh as actual, 
            sum(trip.ev_wh) OVER (ORDER BY trip.start_segmentno) as agg_actual,
            pred.ev_wh as pred, 
            sum(pred.ev_wh) OVER (ORDER BY trip.start_segmentno) as agg_pred,
            osm.startpoint, 
            osm.endpoint, 
            osm.meters,
            rmp10_get_geo(segments) as segmentgeo
        FROM trip_ss trip
        JOIN experiments.rmp10_predictions_finalsupersegmodel_iter1 pred
        ON pred.id = trip.atd_id
        JOIN experiments.rmp10_all_osm_data osm
        ON osm.superseg_id = trip.superseg_id
        OR osm.segmentkey = trip.segmentkey
    ), trip_s AS (
        SELECT *, vit.id as vitid
        FROM mapmatched_data.viterbi_match_osm_dk_20140101 vit
        JOIN experiments.bcj_ev_watt_data wd
        ON wd.id = vit.id
        WHERE trip_id = {0}
        ORDER BY trip_segmentno
    ), trip_vals_s AS (
        SELECT 
            trip.vitid as id,
            trip.trip_segmentno,
            trip.ev_kwh_from_ev_watt * 1000 as actual, 
            sum(trip.ev_kwh_from_ev_watt * 1000) OVER (ORDER BY trip.trip_segmentno) as agg_actual,
             pred.ev_kwh * 1000 as pred, 
            sum(pred.ev_kwh * 1000) OVER (ORDER BY trip.trip_segmentno) as agg_pred,
            osm.startpoint, 
            osm.endpoint, 
            osm.meters,
            osm.segmentgeo as segmentgeo
        FROM trip_s trip
        JOIN experiments.rmp10_predictions_defaultenergy_epochs_20 pred
        ON pred.mapmatched_id = trip.vitid
        JOIN maps.osm_dk_20140101 osm
        ON osm.segmentkey = trip.segmentkey
    ), trip_vals_s_emb AS (
        SELECT 
            trip.vitid as id,
            trip.trip_segmentno,
            trip.ev_kwh_from_ev_watt * 1000 as actual, 
            sum(trip.ev_kwh_from_ev_watt * 1000) OVER (ORDER BY trip.trip_segmentno) as agg_actual,
             pred.ev_kwh * 1000 as pred, 
            sum(pred.ev_kwh * 1000) OVER (ORDER BY trip.trip_segmentno) as agg_pred,
            osm.startpoint, 
            osm.endpoint, 
            osm.meters,
            osm.segmentgeo as segmentgeo
        FROM trip_s trip
        JOIN experiments.rmp10_predictions_bestmodel pred
        ON pred.mapmatched_id = trip.vitid
        JOIN maps.osm_dk_20140101 osm
        ON osm.segmentkey = trip.segmentkey
    ), trip_vals_baseline AS (
        SELECT
            trip.vitid as id,
            trip.trip_segmentno,
            trip.ev_kwh_from_ev_watt * 1000 as actual, 
            sum(trip.ev_kwh_from_ev_watt * 1000) OVER (ORDER BY trip.trip_segmentno) as agg_actual,
             pred.ev_wh as pred, 
            sum(pred.ev_wh) OVER (ORDER BY trip.trip_segmentno) as agg_pred,
            osm.startpoint, 
            osm.endpoint, 
            osm.meters,
            osm.segmentgeo as segmentgeo
        FROM trip_s trip
        JOIN experiments.rmp10_baseline_trip_segment_predictions pred
        ON pred.mapmatched_id = trip.vitid
        JOIN maps.osm_dk_20140101 osm
        ON osm.segmentkey = trip.segmentkey
    )
    SELECT 'ss' as model, row_to_json(fc)::text as path
    FROM (
        SELECT
            'FeaturesCollection' as "type",
            array_to_json(array_agg(f)) as "features"
        FROM (
            SELECT
                'Feature' as "type",
                ST_AsGeoJson(segmentgeo::geometry, 6)::json as "geometry",
                json_build_object(
                    'actual', actual,
                    'predicted', pred,
                    'trip_actual', agg_actual,
                    'trip_predicted', agg_pred,
                    'startpoint', startpoint,
                    'endpoint', endpoint,
                    'id', superseg_id,
                    'segmentno', start_segmentno,
                    'length', meters
                )::json as "properties"
            FROM trip_vals_ss
        ) as f
    ) as fc
    UNION
    SELECT 's' as model, row_to_json(fc)::text as path
    FROM (
        SELECT
            'FeaturesCollection' as "type",
            array_to_json(array_agg(f)) as "features"
        FROM (
            SELECT
                'Feature' as "type",
                ST_AsGeoJson(segmentgeo::geometry, 6)::json as "geometry",
                json_build_object(
                    'actual', actual,
                    'predicted', pred,
                    'trip_actual', agg_actual,
                    'trip_predicted', agg_pred,
                    'startpoint', startpoint,
                    'endpoint', endpoint,
                    'id', id,
                    'segmentno', trip_segmentno,
                    'length', meters
                )::json as "properties"
            FROM trip_vals_s
        ) as f
    ) as fc
    UNION
    SELECT 's_emb' as model, row_to_json(fc)::text as path
    FROM (
        SELECT
            'FeaturesCollection' as "type",
            array_to_json(array_agg(f)) as "features"
        FROM (
            SELECT
                'Feature' as "type",
                ST_AsGeoJson(segmentgeo::geometry, 6)::json as "geometry",
                json_build_object(
                    'actual', actual,
                    'predicted', pred,
                    'trip_actual', agg_actual,
                    'trip_predicted', agg_pred,
                    'startpoint', startpoint,
                    'endpoint', endpoint,
                    'id', id,
                    'segmentno', trip_segmentno,
                    'length', meters
                )::json as "properties"
            FROM trip_vals_s_emb
        ) as f
    ) as fc
    UNION
    SELECT 'base' as model, row_to_json(fc)::text as path
    FROM (
        SELECT
            'FeaturesCollection' as "type",
            array_to_json(array_agg(f)) as "features"
        FROM (
            SELECT
                'Feature' as "type",
                ST_AsGeoJson(segmentgeo::geometry, 6)::json as "geometry",
                json_build_object(
                    'actual', actual,
                    'predicted', pred,
                    'trip_actual', agg_actual,
                    'trip_predicted', agg_pred,
                    'startpoint', startpoint,
                    'endpoint', endpoint,
                    'id', id,
                    'segmentno', trip_segmentno,
                    'length', meters
                )::json as "properties"
            FROM trip_vals_baseline
        ) as f
    ) as fc;
    """.format(trip_id)


def main(args):
    if len(args) < 1:
        print("You must specify a trip id!")
    trip_id = int(args[0])
    qry = get_qry(trip_id)
    res = query(qry)
    print("test")

    if not os.path.exists(os.path.abspath(path + str(trip_id) + "/")):
        try:
            os.makedirs(os.path.abspath(path + str(trip_id) + "/"))
        except OSError as exc: # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise

    for mod in res:
        with open(path + str(trip_id) + "/" + "trip" + str(trip_id) + "-" + tl[mod['model']] + ".json", "w") as f:
            f.write(mod['path'])


if __name__ == '__main__':
    main(sys.argv[1:])
