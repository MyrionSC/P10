import sys
import os
import json
from Configuration import model_path
from DNNSegmentPredictor import create_segment_predictions
import psycopg2
from LocalSettings import local_db
import time


def exec(qrys):
    conn = psycopg2.connect(
        "dbname='{0}' user='{1}' port='{2}' host='{3}' password='{4}'".format(local_db['name'], local_db['user'],
                                                                              local_db['port'], local_db['host'],
                                                                              local_db['password']))
    cur = conn.cursor()
    for qry in qrys:
        print("Executing query:")
        print(qry)
        start_time = time.time()
        cur.execute(qry)
        print("Time elapsed: %s seconds\n" % (time.time() - start_time))
    print()
    print("Commiting changes.")
    conn.commit()
    cur.close()
    conn.close()


if __name__ == "__main__":
    args = sys.argv[1:]

    if len(args) != 2:
        print("Invalid number of arguments: " + str(len(args)))
        print("Expected 2")
        quit()

    modelpath = args[0].strip()
    if not os.path.isdir(modelpath):
        print("Specified model does not exist")
        quit()

    tablename = args[1].strip()

    print("Loading model configuration")
    with open(modelpath + "config.json", "r") as f:
        config = json.load(f)
    if not os.path.isfile(model_path(config) + "segment_predictions.csv"):
        print("No predictions present: Generating")
        create_segment_predictions(config)

    table_qry = """
        DROP TABLE IF EXISTS models.{0};
        
        CREATE TABLE models.{0} (
            segmentkey bigint,
            direction functionality.driving_direction,
            cost float
        );
    """.format(tablename)

    copy_qry = """
        COPY models.{0} (segmentkey, direction, cost) 
        FROM '{1}' 
        DELIMITER ';' 
        CSV HEADER 
        ENCODING 'UTF8';
    """.format(tablename, os.path.abspath(model_path(config) + "segment_predictions.csv"))

    index_qry = """
        CREATE INDEX models_{0}_segmentkey_direction_idx
            ON models.{0} USING btree
            (segmentkey, direction)
            TABLESPACE pg_default;
            
        CREATE INDEX models_{0}_segmentkey_idx
            ON models.{0} USING btree
            (segmentkey)
            TABLESPACE pg_default;
    """.format(tablename)

    exec([table_qry, copy_qry, index_qry])
