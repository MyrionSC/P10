import psycopg2
from psycopg2.extras import RealDictCursor
import pandas as pd
from db_settings import *

dijkstra_qry = '\'SELECT segmentkey as id, startpoint as source, endpoint as target, segmentgeom as the_geom, length as cost FROM maps.routing2\''

def query(str, db):
    conn = psycopg2.connect("dbname='{0}' user='{1}' port='{2}' host='{3}' password='{4}'".format(db['name'], db['user'], db['port'], db['host'], db['password']))
    cur = conn.cursor()
    cur.execute(str)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

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
                    ST_AsGeoJSON(segmentgeom, 6) :: json as "geometry"
                FROM (
                    SELECT
                        segmentgeom
                    FROM pgr_dijkstra({2}::text, {0}::bigint, {1}::bigint) pgr
                    JOIN maps.routing osm
                    ON pgr.edge = osm.segmentkey
                ) as q
            ) as f
        ) as fc
    """.format(origin, dest, dijkstra_qry)
    return query(qry, local_db)[0][0]

def get_embedding(key):
	qry = """
		SELECT *
		FROM embeddings.line
		WHERE segmentkey = {0}
	""".format(key)
	return str(list(query(qry, local_db)[0])[1:])