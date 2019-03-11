import psycopg2
from db_settings import *
from Utilities.Model import load_model
from Configuration import energy_config

model = load_model(energy_config)


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
                    json_build_object('cost', cost, 'agg_cost', agg_cost, 'length', length, 'agg_length', agg_length, 'segmentkey', segmentkey) :: json as "properties"
                FROM (
                    SELECT
                        osm.segmentkey, segmentgeom, pgr.cost, pgr.agg_cost, length, sum(length) OVER (ORDER BY pgr.path_seq) as agg_length
                    FROM pgr_dijkstra({2}::text, {0}::bigint, {1}::bigint) pgr
                    JOIN maps.routing osm
                    ON pgr.edge = osm.segmentkey
                ) as q
            ) as f
        ) as fc
    """.format(origin, dest, dijkstra_qry(model))


def query(qry, db):
    conn = psycopg2.connect("dbname='{0}' user='{1}' port='{2}' host='{3}' password='{4}'".format(db['name'], db['user'], db['port'], db['host'], db['password']))
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