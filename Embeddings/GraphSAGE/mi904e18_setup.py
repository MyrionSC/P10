#!/usr/bin/python3
#
# Creates node embedings using structure of the graph and
#       segment length, categoryid and incline_angle; 
#
import networkx as nx
from networkx.readwrite import json_graph
import json
import psycopg2
from psycopg2.extras import RealDictCursor
import pandas as pd
import numpy as np
import os
import tensorflow as tf
import random

from LocalSettings import database

tf.set_random_seed(1337)
random.seed(1337)
np.random.seed(1337)

N_WALKS = 5  # number of random walks per node


def sql_query(str):
    conn = psycopg2.connect(f"dbname='{database['name']}' user='{database['user']}' port='{database['port']}' host='{database['host']}' password='{database['password']}'")
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute(str)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


def create_graph(dir):
    print('Creating Graph...', end='')
    queryreversed = """
        SELECT edge_id, startpoint, endpoint, node_id FROM experiments.mi904e18_node_transform
    """

    reversedata = sql_query(queryreversed)
    G = nx.Graph()

    for record in reversedata:
        node1 = record['startpoint']
        node2 = record['endpoint']
        G.add_node(node1, val=False, test=False)
        G.add_node(node2, val=False, test=False)
        G.add_edge(node1, node2, weight=1)

    js_graph = json_graph.node_link_data(G)

    with open(os.path.join(dir, 'mi904e18-G.json'), 'w') as file:
        json.dump(js_graph, file)
    print('Done.')


def create_id_map(dir):
    print('Creating mapping...', end='')
    # load graph

    with open(os.path.join(dir, 'mi904e18-G.json')) as file:
        js_graph = json.load(file)
        G = json_graph.node_link_graph(js_graph)

    # list all nodes
    segments_dict = {}
    for i, node in enumerate(G.nodes()):
        segments_dict[str(node)] = i

    with open(os.path.join(dir, 'mi904e18-id_map.json'), 'w') as file:
        json.dump(segments_dict, file)
    print('Done')


def create_feats_file(dir):
    print('Creating features file...', end='')
    # create *-feats.npy file
    features_query = """
        SELECT maps_table.segmentkey,
               maps_table.meters,
               maps_table.categoryid,
               CASE WHEN incline_table.incline_angle IS NULL THEN 0.0
                    ELSE incline_table.incline_angle END AS incline_angle
        FROM maps.osm_dk_20140101 AS maps_table
        LEFT JOIN experiments.mi904e18_segment_incline AS incline_table
        ON (maps_table.segmentkey = incline_table.segmentkey)
        ORDER BY maps_table.segmentkey ASC
    """

    features_data = sql_query(features_query)

    df = pd.DataFrame(features_data)
    df.set_index('segmentkey', inplace=True)

    with open(os.path.join(dir, 'mi904e18-id_map.json')) as file:
        order_map = json.load(file)

    order_list = [None] * len(order_map)
    for key, value in order_map.items():
        order_list[value] = int(key)

    df = df.reindex(order_list)  # change dataframe ordering to the one specified in *-id_map.json

    # sanity checks
    assert df.isnull().values.any() == False  # True if any of the cells has NaN value
    assert df.shape[0] == len(order_list)  # check if DataFrame length didn't changed

    # perform one-hot encoding
    df['categoryid'] = df['categoryid'].astype('category')

    one_hot = pd.get_dummies(df['categoryid'], prefix='categoryid')
    df = df.drop('categoryid', axis=1)
    df = df.join(one_hot)

    # save features to file
    np.save(os.path.join(dir, 'mi904e18-feats.npy'), df.values, allow_pickle=False)
    print('Done')


def create_class_file(dir):
    print('Creating class label file...', end='')
    # load graph
    with open(os.path.join(dir, 'mi904e18-G.json')) as file:
        js_graph = json.load(file)
        G = json_graph.node_link_graph(js_graph)

    # create *-class_map.json
    class_map = {}
    for node in G.nodes():
        class_map[str(node)] = 1

    with open(os.path.join(dir, 'mi904e18-class_map.json'), 'w') as file:
        json.dump(class_map, file)
    print('Done')


def create_walks(dir):
    with open(os.path.join(dir, 'mi904e18-G.json')) as file:
        js_graph = json.load(file)
        G = json_graph.node_link_graph(js_graph)

    from graphsage.utils import run_random_walks

    pairs = run_random_walks(G, G.nodes(), num_walks=N_WALKS)

    with open(os.path.join(dir, 'mi904e18-walks.txt'), "w") as fp:
        fp.write("\n".join([str(p[0]) + "\t" + str(p[1]) for p in pairs]))


def create_embeddings_csv(model_dir, output_dir):
    print('Creating embeddings...', end='')
    embeddings = np.load(os.path.join(model_dir, 'val.npy'))

    df = pd.DataFrame(embeddings, columns=['embedding_%d' % i for i in range(embeddings.shape[1])])

    # reorder embeddings
    embeddings_order = []
    with open(os.path.join(model_dir, 'val.txt'), 'r') as file:
        content = file.readlines()
        content = [x.strip() for x in content]
        for segmentkey in content:
            embeddings_order.append(int(segmentkey))

    df['segmentkey'] = pd.Series(embeddings_order, dtype=np.int64)
    df = df.set_index('segmentkey')

    # sanity checks
    assert df.isnull().values.any() == False  # True if any of the cells has NaN value
    assert df.shape[0] == embeddings.shape[0]  # check if DataFrame length didn't changed
    assert df.shape[0] == len(embeddings_order)  # check if DataFrame length didn't changed
    
    df = df.sort_values(by='segmentkey')
    df.to_csv(os.path.join(output_dir, 'mi904e18-embeddings.csv'), sep=' ')
    print('Done.')


if __name__ == '__main__':

    assert nx.__version__ == '1.11'  # sanity check

    if not os.path.exists('./mi904e18_data/'):
        os.makedirs('./mi904e18_data/')

    assert os.path.exists('./mi904e18_data/') == True  # sanity check

    data_dir = './mi904e18_data'

    # Creates a graph where edges are nodes and nodes are edges.
    # This is to allow for embedding the edges with a node embedding algorithm.
    create_graph(data_dir)  # create *-G-json file (graph)

    create_id_map(data_dir)  # create *-id_map.json file (mapping bewteen nodes in the graph and features)

    create_feats_file(data_dir)  # create *-feats.npy (features numpy file)

    create_class_file(data_dir)  # create *-class_map.json (mapping classes to nodes)

    create_walks(data_dir)  # create *-walks.txt (random walks file)

    # sanity checks
    assert os.path.isfile('./mi904e18_data/mi904e18-G.json')  # graph file
    assert os.path.isfile('./mi904e18_data/mi904e18-id_map.json')  # ID mapping file
    assert os.path.isfile('./mi904e18_data/mi904e18-feats.npy')  # features file
    assert os.path.isfile('./mi904e18_data/mi904e18-class_map.json')  # class mapping file
    assert os.path.isfile('./mi904e18_data/mi904e18-walks.txt')  # random walks file

    # run model
    import graphsage.unsupervised_train as GraphSAGE
    import tensorflow as tf

    tf.app.run(GraphSAGE.main, argv=[os.path.basename(__file__),
                                     '--train_prefix', 'mi904e18_data/mi904e18',
                                     '--model', 'graphsage_mean',
                                     '--dim_1', '16',
                                     '--dim_2', '16',
                                     '--max_total_steps', '1000000',
                                     '--model_size', 'big',
                                     '--identity_dim', '32'])

    # create .csv file for embeddings
    create_embeddings_csv('./unsup-mi904e18_data/graphsage_mean_big_0.00001_identity_32', 'mi904e18_data/')
