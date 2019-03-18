import psycopg2
from Utils.LocalSettings import *
from psycopg2.extras import RealDictCursor
import pandas as pd

chosen_model = 'no_time'


def dijkstra_qry(model=chosen_model):
    if model == 'baseline':
        return '\'SELECT rou.segmentkey as id, startpoint as source, endpoint as target, segmentgeom as the_geom, model.cost / 1000 + 1 as cost FROM maps.routing3 rou JOIN models.{0} model ON model.segmentkey = rou.segmentkey AND model.direction = rou.direction\''.format(model)
    else:
        return '\'SELECT rou.segmentkey as id, startpoint as source, endpoint as target, segmentgeom as the_geom, model.cost + 1 as cost FROM maps.routing3 rou JOIN models.{0} model ON model.segmentkey = rou.segmentkey AND model.direction = rou.direction\''.format(model)


def routing_qry(origin, dest, model=chosen_model):
    return """
    	SELECT row_to_json(fc)::text as path
        FROM(
            SELECT
                'FeaturesCollection' as "type",
                array_to_json(array_agg(f)) as "features"
            FROM (
                SELECT
                    'Feature' as "type",
                    ST_AsGeoJSON(segmentgeom, 6) :: json as "geometry",
                    json_build_object(
                        'cost', cost, 
                        'agg_cost', agg_cost,
                        'length', length,
                        'agg_length', agg_length,
                        'segmentkey', segmentkey,
                        'direction', direction,
                        'startpoint', startpoint,
                        'endpoint', endpoint
                    ) :: json as "properties"
                FROM (
                    SELECT
                        osm.segmentkey, 
                        segmentgeom, 
                        pgr.cost, 
                        pgr.agg_cost, 
                        length, 
                        sum(length) OVER (ORDER BY pgr.path_seq) as agg_length,
                        CASE WHEN pgr.node = osm.startpoint
                             THEN 'FORWARD'::functionality.direction_driving
                             ELSE 'BACKWARD'::functionality.direction_driving
                        END AS direction,
                        osm.startpoint,
                        osm.endpoint
                    FROM pgr_dijkstra({2}::text, {0}::bigint, {1}::bigint) pgr
                    JOIN maps.routing osm
                    ON pgr.edge = osm.segmentkey
                ) as q
            ) as f
        ) as fc
    """.format(origin, dest, dijkstra_qry(model))


def query(qry, db, cursor=None):
    conn = psycopg2.connect("dbname='{0}' user='{1}' port='{2}' host='{3}' password='{4}'".format(db['name'], db['user'], db['port'], db['host'], db['password']))
    if cursor is not None:
        cur = conn.cursor(cursor_factory=cursor)
    else:
        cur = conn.cursor()
    cur.execute(qry)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


def get_route(origin, dest):
    return query(routing_qry(origin, dest, chosen_model), local_db)[0][0]


def get_baseline(origin, dest):
    return query(routing_qry(origin, dest, 'baseline'), local_db)[0][0]


def get_embedding(key):
	qry = """
		SELECT *
		FROM embeddings.line
		WHERE segmentkey = {0}
	""".format(key)
	return str(list(query(qry, local_db)[0])[1:])


def get_weather_station(segmentkey: int) -> str:
    qry = """
    	SELECT wsname
    	FROM weather.segment_weatherstation_map
    	WHERE segmentkey = {0}
    """.format(segmentkey)
    return query(qry, local_db)[0][0]


def get_baseline_and_actual(trip_id):
    qry = """
        SELECT 
            vit.id, 
            preds.ev_wh / 1000 as baseline, 
            sum(preds.ev_wh / 1000) OVER (ORDER BY vit.trip_segmentno) as agg_baseline,
            CASE WHEN vit.ev_kwh IS NOT NULL
                 THEN vit.ev_kwh
                 ELSE 0.0
            END as actual,
            sum(vit.ev_kwh) OVER (ORDER BY vit.trip_segmentno) as agg_actual
        FROM mapmatched_data.viterbi_match_osm_dk_20140101 vit
        JOIN experiments.rmp10_baseline_segment_predictions preds
        ON vit.segmentkey = preds.segmentkey
        WHERE vit.trip_id = {0}
        ORDER BY vit.trip_segmentno
    """.format(trip_id)
    return pd.DataFrame(query(qry, main_db, cursor=RealDictCursor))
