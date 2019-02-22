import networkx as nx
import psycopg2
from psycopg2.extras import RealDictCursor

from LocalSettings import main_db

def sql_query(str):
    conn = psycopg2.connect("dbname='{0}' user='{1}' port='{2}' host='{3}' password='{4}'".format(main_db['name'], main_db['user'], main_db['port'], main_db['host'], main_db['password']))
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute(str)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

querynormal = """
SELECT segmentkey, startpoint, endpoint, direction FROM maps.osm_dk_20140101
"""

queryreversed = """
SELECT edge_id, startpoint, endpoint, node_id FROM experiments.mi904e18_node_transform
"""
data = sql_query(querynormal)
reversedata=sql_query(queryreversed)
print("First in normal:", data[:1])
print("First in reverse:", reversedata[:1])
G = nx.DiGraph()
G2 = nx.Graph()

for record in data:
    startpoint = record['startpoint']
    endpoint = record['endpoint']
    direction = record['direction']
    G.add_node(startpoint)
    G.add_node(endpoint)
    if direction != 'BOTH':
        G.add_edge(startpoint, endpoint, weight=1)
    else:
        G.add_edge(startpoint, endpoint, weight=1)
        G.add_edge(endpoint, startpoint, weight=1)
nx.write_edgelist(G, 'osm_dk_20140101.edges')

# Creates a graph like the above, where edges are nodes and nodes are edges.
# This is to allow for embedding the edges with a node embedding algorithm.
for record in reversedata:
    node1 = record['startpoint']
    node2 = record['endpoint']
    G2.add_node(node1)
    G2.add_node(node2)
    G2.add_edge(node1, node2, weight=1)
nx.write_edgelist(G2, 'osm_dk_20140101-transformed.edges')