import psycopg2
from psycopg2.extras import RealDictCursor
import pandas as pd

database = {
    "name": "ev_smartmi",
    "user": "smartmi",
    "port": "4102",
    "host": "172.19.1.104",
    "password": "63p467R=530"
}

def query(str):
    conn = psycopg2.connect("dbname='{0}' user='{1}' port='{2}' host='{3}' password='{4}'".format(database['name'], database['user'], database['port'], database['host'], database['password']))
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute(str)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

qry = """
	SELECT startpoint, endpoint, meters as weight FROM experiments.mi904e18_node_transform
"""

df = pd.DataFrame(query(qry))

df.to_csv('line_input.csv', sep=" ", header=False, index=False)
