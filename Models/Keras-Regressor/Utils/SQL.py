import psycopg2
from psycopg2.extras import RealDictCursor
import time
from typing import List
import math
from Utils.LocalSettings import main_db
import pandas as pd
import numpy as np

month = '3'
quarter = '35'
hour = str(math.floor(int(quarter) / 4))
two_hour = hour = str(math.floor(int(hour) / 2))
four_hour = hour = str(math.floor(int(hour) / 4))
six_hour = hour = str(math.floor(int(hour) / 6))
twelve_hour = hour = str(math.floor(int(hour) / 12))
weekday = '3'


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
        cur.copy_from(file, "experiments.rmp10_latest_candidate_prediction", sep=",", columns=('id', 'prediction'))
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


def road_map_qry(segmentkeys=None, directions=None):
    order_string = "" if segmentkeys is None else """
        LEFT JOIN unnest(ARRAY[{0}]::int[]) WITH ORDINALITY o(segmentkey, ord) USING (segmentkey)
        ORDER BY o.ord;
    """.format(", ".join([str(x) for x in segmentkeys]))

    forwards = []
    backwards = []
    for i in range(len(directions)):
        if directions[i] == 'FORWARD':
            forwards.append(segmentkeys[i])
        else:
            backwards.append(segmentkeys[i])

    return """
        SELECT x.*
        FROM (
            SELECT 
                osm.segmentkey,
                ST_AsGeoJson(osm.segmentgeo) as segmentgeo,
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
                osm.categoryid
            FROM maps.osm_dk_20140101 osm
            FULL OUTER JOIN experiments.mi904e18_speedlimits sl
            ON sl.segmentkey = osm.segmentkey
            FULL OUTER JOIN experiments.mi904e18_segment_incline inc
            ON inc.segmentkey = osm.segmentkey
            WHERE osm.category != 'ferry' {0}
            UNION
            SELECT 
                osm.segmentkey,
                ST_AsGeoJson(osm.segmentgeo) as segmentgeo,
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
                osm.categoryid
            FROM maps.osm_dk_20140101 osm
            FULL OUTER JOIN experiments.mi904e18_speedlimits sl
            ON sl.segmentkey = osm.segmentkey
            FULL OUTER JOIN experiments.mi904e18_segment_incline inc
            ON inc.segmentkey = osm.segmentkey
            WHERE osm.category != 'ferry' AND osm.direction = 'BOTH' {1}
        ) as x
        {2}
    """.format(
        "" if segmentkeys is None else "AND osm.segmentkey=ANY(ARRAY[" + ", ".join([str(x) for x in forwards]) + "]::int[])",
        "" if segmentkeys is None else "AND osm.segmentkey=ANY(ARRAY[" + ", ".join([str(x) for x in backwards]) + "]::int[])",
        order_string
    )


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


def get_route(segmentkeys, directions):
    qry = """
        SELECT
            osm_map.segmentkey as segmentkey,
            osm_map.categoryid,
            CASE WHEN incline_table.incline IS NOT NULL
                 THEN incline_table.incline
                 ELSE 0
            END AS height_change,
            CASE WHEN incline_table.incline_percentage IS NOT NULL
                 THEN incline_table.incline_percentage
                 ELSE 0
            END AS incline,
            osm_map.meters as segment_length,
            10::smallint as temperature,
            {0}::smallint as quarter,
            {1}::smallint as hour,
            {2}::smallint as two_hour,
            {3}::smallint as four_hour,
            {4}::smallint as six_hour,
            {5}::smallint as twelve_hour,
            {6}::smallint as weekday,
            {7}::smallint as month,
            speedlimit_table.speedlimit
        FROM maps.osm_dk_20140101 as osm_map,
            experiments.mi904e18_segment_incline as incline_table,
            experiments.mi904e18_speedlimits as speedlimit_table
        WHERE osm_map.segmentkey = ANY(ARRAY[{8}])
        AND osm_map.segmentkey = incline_table.segmentkey
        AND osm_map.segmentkey = speedlimit_table.segmentkey;
    """.format(
        quarter,
        hour,
        two_hour,
        four_hour,
        six_hour,
        twelve_hour,
        weekday,
        month,
        ", ".join([str(x) for x in segmentkeys])
    )
    df = pd.DataFrame(read_query(qry, main_db))
    df = pd.merge(df, pd.DataFrame({'direction': directions, 'segmentkey': segmentkeys}), left_on='segmentkey',
                  right_on='segmentkey')
    df['height_change'] = np.where(df['direction'] == "FORWARD", df['height_change'], -df['height_change'])
    df['incline'] = np.where(df['direction'] == "FORWARD", df['incline'], -df['incline'])
    df.drop(['direction'], axis=1, inplace=True)
    return df


def get_predicting_base_data_qry(trip_ids=None):
    if trip_ids is not None:
        string = "trips_table.trip_id = ANY(ARRAY[{0}])\n\t\tAND".format(", ".join([str(x) for x in trip_ids]))
    else:
        string = ""

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
            trips_table.direction,
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
            speedlimit_table.speedlimit
        FROM experiments.mi904e18_training as trips_table, 
            maps.osm_dk_20140101 as osm_map,
            dims.dimdate as date_table, 
            dims.dimtime as time_table, 
            experiments.mi904e18_segment_incline as incline_table,
            dims.dimweathermeasure as weather_table, 
            experiments.mi904e18_wind_vectors as wind_table,
            experiments.mi904e18_speedlimits as speedlimit_table
        WHERE {0} trips_table.segmentkey = osm_map.segmentkey 
        AND trips_table.datekey = date_table.datekey 
        AND trips_table.timekey = time_table.timekey 
        AND trips_table.segmentkey = incline_table.segmentkey
        AND trips_table.weathermeasurekey = weather_table.weathermeasurekey
        AND trips_table.id = wind_table.vector_id
        AND trips_table.segmentkey = speedlimit_table.segmentkey;
    """.format(string)
