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


def copy_latest_preds_transaction(path, db):
    conn = psycopg2.connect(
        "dbname='{0}' user='{1}' port='{2}' host='{3}' password='{4}'".format(db['name'], db['user'],
                                                                              db['port'], db['host'],
                                                                              db['password']))
    cur = conn.cursor()
    cur.execute(delete_latest_predictions_qry())
    with open(path, "r") as file:
        cur.copy_from(file, "experiments.rmp10_latest_prediction", sep=",", columns=('id', 'prediction'))
    conn.commit()
    cur.close()
    conn.close()


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
    if not path[:-1] == "/":
        path += "/"
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


def get_trip_info(trip_id, db):
    tripSegsQuery = """
        select *
        from mapmatched_data.viterbi_match_osm_dk_20140101
        where trip_id={0}
        ORDER by trip_segmentno
    """.format(trip_id)
    tripMetaQuery = """
        select *
        from mapmatched_data.viterbi_meta_osm_dk_20140101
        where trip_id={0}
    """.format(trip_id)
    tripsegs = read_query(tripSegsQuery, db)
    meta = read_query(tripMetaQuery, db)
    return tripsegs, meta


def delete_latest_predictions_qry():
    return """
        DELETE FROM experiments.rmp10_latest_prediction;
    """


def get_existing_trips(trip_ids):
    return """
        SELECT
            trips_table.trip_id as trip_id,
            ST_AsGeoJson(osm_map.segmentgeo) as segmentgeo,
            trips_table.trip_segmentno as trip_segmentno,
            trips_table.id as mapmatched_id,
            trips_table.segmentkey as segmentkey,
            osm_map.categoryid,
            CASE WHEN incline_table.incline_percentage IS NOT NULL
                 THEN CASE WHEN trips_table.direction = 'BACKWARD'
                           THEN -incline_table.incline
                           ELSE incline_table.incline
                      END 
                 ELSE 0
            END AS height_change,
            CASE WHEN incline_table.incline_percentage IS NOT NULL
                 THEN CASE WHEN trips_table.direction = 'BACKWARD'
                           THEN -incline_table.incline_percentage
                           ELSE incline_table.incline_percentage
                      END 
                 ELSE 0
            END AS incline,
            trips_table.meters_segment as segment_length,
            trips_table.speed / 3.6 as speed,
            weather_table.air_temperature as temperature,
            CASE WHEN wind_table.tailwind_magnitude IS NOT NULL
                 THEN -wind_table.tailwind_magnitude 
                 ELSE 0
            END as headwind_speed,
            time_table.quarter,
            time_table.hour,
            (time_table.hour / 2)::smallint as two_hour,
            (time_table.hour / 4)::smallint as four_hour,
            (time_table.hour / 6)::smallint as six_hour,
            (time_table.hour / 12)::smallint as twelve_hour,
            date_table.weekday,
            date_table.month,
            CASE WHEN trips_table.ev_kwh IS NOT NULL
                 THEN trips_table.ev_kwh
                 ELSE 0.0
            END AS ev_kwh,
            speedlimit_table.speedlimit,
            CASE WHEN inter_table.intersection THEN 1 ELSE 0 END as intersection
        FROM experiments.mi904e18_training as trips_table, 
            maps.osm_dk_20140101 as osm_map,
            dims.dimdate as date_table, 
            dims.dimtime as time_table, 
            experiments.mi904e18_segment_incline as incline_table,
            dims.dimweathermeasure as weather_table, 
            experiments.mi904e18_wind_vectors as wind_table,
            experiments.mi904e18_speedlimits as speedlimit_table,
            experiments.rmp10_intersections as inter_table
        WHERE trips_table.trip_id = ANY(ARRAY[{0}])
        AND trips_table.segmentkey = osm_map.segmentkey 
        AND trips_table.datekey = date_table.datekey 
        AND trips_table.timekey = time_table.timekey 
        AND trips_table.segmentkey = incline_table.segmentkey
        AND trips_table.weathermeasurekey = weather_table.weathermeasurekey
        AND trips_table.id = wind_table.vector_id
        AND trips_table.segmentkey = inter_table.segmentkey
        AND trips_table.segmentkey = speedlimit_table.segmentkey;
    """.format(", ".join([str(x) for x in trip_ids]))
