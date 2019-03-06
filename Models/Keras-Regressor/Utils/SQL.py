import psycopg2
from psycopg2.extras import RealDictCursor
import time
from typing import List


# Execute a read query against the database
def read_query(qry: str, db: dict):
    conn = psycopg2.connect(
        "dbname='{0}' user='{1}' port='{2}' host='{3}' password='{4}'".format(db['name'], db['user'],
                                                                              db['port'], db['host'],
                                                                              db['password']))
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute(qry)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


def write_transaction(qrys: List[str], db: dict):
    conn = psycopg2.connect(
        "dbname='{0}' user='{1}' port='{2}' host='{3}' password='{4}'".format(db['name'], db['user'],
                                                                              db['port'], db['host'],
                                                                              db['password']))
    cur = conn.cursor()
    for qry in qrys:
        print("Executing read_query:")
        print(qry)
        start_time = time.time()
        cur.execute(qry)
        print("Time elapsed: %s seconds\n" % (time.time() - start_time))
    print()
    print("Commiting changes.")
    conn.commit()
    cur.close()
    conn.close()


def supersegment_qry(num_segments, limit=None):
    qrt = "SELECT\n\ts1.trip_id,\n\ts1.trip_segmentno as supersegmentno,\n\t"
    qrt += ",\n\t".join([
        "s{0}.segmentkey as key{0},\n\ts{0}.categoryid as category{0},\n\ts{0}.meters as segment{0}_length".format(
            i + 1) for i in range(num_segments)])
    qrt += ",\n\t" + " + ".join(
        ["s{0}.meters".format(i + 1) for i in range(num_segments)]) + " as supersegment_length\n"
    qrt += "FROM experiments.rmp10_supersegment_info as s1\n"
    qrt += "\n".join([
        "JOIN experiments.rmp10_supersegment_info as s{1}\nON s{0}.trip_id = s{1}.trip_id \nAND s{1}.trip_segmentno = s{0}.trip_segmentno + 1".format(
            i, i + 1) for i in range(1, num_segments)])
    qrt += "\nORDER BY trip_id, supersegmentno"
    if limit is not None and isinstance(limit, int):
        qrt += "\nLIMIT " + str(limit)
    return qrt


def road_map_qry():
    return """
        SELECT 
            osm.segmentkey,
            CASE WHEN inc.incline IS NOT NULL 
                 THEN inc.incline
                 ELSE 0 
            END as height_change,
            CASE WHEN inc.incline IS NOT NULL
                 THEN inc.incline_percentage
                 ELSE 0
            END as incline,
            'FORWARD' as direction,
            osm.meters as segment_length, 
            sl.speedlimit, 
            osm.categoryid,
            CASE WHEN inter.intersection THEN 1 ELSE 0 END as intersection
        FROM maps.osm_dk_20140101 osm
        FULL OUTER JOIN experiments.mi904e18_speedlimits sl
        ON sl.segmentkey = osm.segmentkey
        FULL OUTER JOIN experiments.mi904e18_segment_incline inc
        ON inc.segmentkey = osm.segmentkey
        FULL OUTER JOIN experiments.rmp10_intersections inter
        ON inter.segmentkey = osm.segmentkey
        WHERE osm.category != 'ferry'
        UNION
        SELECT 
            osm.segmentkey,
            CASE WHEN inc.incline IS NOT NULL 
                 THEN -inc.incline
                 ELSE 0 
            END as height_change,
            CASE WHEN inc.incline IS NOT NULL
                 THEN -inc.incline_percentage
                 ELSE 0
            END as incline,
            'BACKWARD' as direction,
            osm.meters as segment_length, 
            sl.speedlimit, 
            osm.categoryid,
            CASE WHEN inter.intersection THEN 1 ELSE 0 END as intersection
        FROM maps.osm_dk_20140101 osm
        FULL OUTER JOIN experiments.mi904e18_speedlimits sl
        ON sl.segmentkey = osm.segmentkey
        FULL OUTER JOIN experiments.mi904e18_segment_incline inc
        ON inc.segmentkey = osm.segmentkey
        FULL OUTER JOIN experiments.rmp10_intersections inter
        ON inter.segmentkey = osm.segmentkey
        WHERE osm.category != 'ferry' AND osm.direction = 'BOTH'
    """


def average_weather_qry(month, quarter):
    return """
        SELECT
            avg(air_temperature) as temperature,
            avg(-wind.tailwind_magnitude) as headwind_speed
        FROM mapmatched_data.viterbi_match_osm_dk_20140101 vit
        JOIN experiments.mi904e18_wind_vectors wind
        ON wind.vector_id = vit.id
        JOIN dims.dimdate dat
        ON vit.datekey = dat.datekey
        JOIN dims.dimtime tim
        ON vit.timekey = tim.timekey
        JOIN dims.dimweathermeasure wea
        ON vit.weathermeasurekey = wea.weathermeasurekey
        WHERE dat.month = {0}
        AND tim.quarter = {1}
    """.format(month, quarter)


def table_qry(tablename):
    return """
        DROP TABLE IF EXISTS models.{0};

        CREATE TABLE models.{0} (
            segmentkey bigint,
            direction functionality.direction_driving,
            cost float
        );
    """.format(tablename)


def copy_qry(tablename, path):
    return """
        COPY models.{0} (segmentkey, direction, cost) 
        FROM '{1}' 
        DELIMITER ';' 
        CSV HEADER 
        ENCODING 'UTF8';
    """.format(tablename, path + "segment_predictions.csv")


def index_qry(tablename):
    return """
        CREATE INDEX models_{0}_segmentkey_direction_idx
            ON models.{0} USING btree
            (segmentkey, direction)
            TABLESPACE pg_default;

        CREATE INDEX models_{0}_segmentkey_idx
            ON models.{0} USING btree
            (segmentkey)
            TABLESPACE pg_default;
    """.format(tablename)