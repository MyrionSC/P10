CREATE EXTENSION postgis;
CREATE EXTENSION pgrouting;

CREATE SCHEMA embeddings
    AUTHORIZATION postgres;

CREATE SCHEMA maps
    AUTHORIZATION postgres;

CREATE SCHEMA functionality
    AUTHORIZATION postgres;

CREATE TABLE maps.osm_dk_20140101
(
    segmentkey integer NOT NULL,
    startpoint integer,
    endpoint integer,
    meters real,
    category functionality.osm_categories,
    direction functionality.direction_map,
    categoryid smallint,
    speedlimit_forward smallint,
    speedlimit_backward smallint,
    logprime bigint NOT NULL,
    segmentgeo geography,
    name text COLLATE pg_catalog."default",
    CONSTRAINT osm_dk_20140101_pkey PRIMARY KEY (segmentkey)
        WITH (FILLFACTOR=100)
)
WITH (
    OIDS = FALSE,
    FILLFACTOR = 100
)
TABLESPACE pg_default;

CREATE INDEX osm_dk_20140101_category_idx
    ON maps.osm_dk_20140101 USING btree
    (category)
    WITH (FILLFACTOR=100)
    TABLESPACE pg_default;

CREATE INDEX osm_dk_20140101_categoryid_idx
    ON maps.osm_dk_20140101 USING btree
    (categoryid)
    WITH (FILLFACTOR=100)
    TABLESPACE pg_default;

CREATE INDEX osm_dk_20140101_categoryid_idx1
    ON maps.osm_dk_20140101 USING btree
    (categoryid)
    TABLESPACE pg_default;

CREATE INDEX osm_dk_20140101_direction_idx
    ON maps.osm_dk_20140101 USING btree
    (direction)
    WITH (FILLFACTOR=100)
    TABLESPACE pg_default;

CREATE INDEX osm_dk_20140101_endpoint_idx
    ON maps.osm_dk_20140101 USING btree
    (endpoint)
    WITH (FILLFACTOR=100)
    TABLESPACE pg_default;

CREATE INDEX osm_dk_20140101_segmentgeo_25832_index
    ON maps.osm_dk_20140101 USING btree
    (st_transform(segmentgeo::geometry, 25832))
    TABLESPACE pg_default;

CREATE INDEX osm_dk_20140101_segmentgeo_end_index
    ON maps.osm_dk_20140101 USING btree
    (st_endpoint(st_transform(segmentgeo::geometry, 25832)))
    TABLESPACE pg_default;

CREATE INDEX osm_dk_20140101_segmentgeo_idx
    ON maps.osm_dk_20140101 USING gist
    (segmentgeo)
    WITH (FILLFACTOR=100)
    TABLESPACE pg_default;

CREATE INDEX osm_dk_20140101_segmentkey_categoryid_category_direction_me_idx
    ON maps.osm_dk_20140101 USING btree
    (segmentkey, categoryid, category, direction, meters)
    TABLESPACE pg_default;

CREATE INDEX osm_dk_20140101_segmentkey_idx
    ON maps.osm_dk_20140101 USING btree
    (segmentkey)
    TABLESPACE pg_default;

CREATE INDEX osm_dk_20140101_speedlimit_backward_idx
    ON maps.osm_dk_20140101 USING btree
    (speedlimit_backward)
    WITH (FILLFACTOR=100)
    TABLESPACE pg_default;

CREATE INDEX osm_dk_20140101_speedlimit_backward_idx1
    ON maps.osm_dk_20140101 USING btree
    (speedlimit_backward)
    TABLESPACE pg_default;

CREATE INDEX osm_dk_20140101_speedlimit_forward_idx
    ON maps.osm_dk_20140101 USING btree
    (speedlimit_forward)
    WITH (FILLFACTOR=100)
    TABLESPACE pg_default;

CREATE INDEX osm_dk_20140101_speedlimit_forward_idx1
    ON maps.osm_dk_20140101 USING btree
    (speedlimit_forward)
    TABLESPACE pg_default;

CREATE INDEX osm_dk_20140101_start_index
    ON maps.osm_dk_20140101 USING btree
    (st_startpoint(st_transform(segmentgeo::geometry, 25832)))
    TABLESPACE pg_default;

CREATE INDEX osm_dk_20140101_startpoint_idx
    ON maps.osm_dk_20140101 USING btree
    (startpoint)
    WITH (FILLFACTOR=100)
    TABLESPACE pg_default;

COPY maps.osm_dk_20140101 (segmentkey, startpoint, endpoint, meters, category, direction, categoryid, speedlimit_forward, speedlimit_backward, logprime, segmentgeo, name) 
FROM 'maps.csv' 
DELIMITER ';' 
CSV HEADER 
ENCODING 'UTF8' 
QUOTE '\"' 
ESCAPE '''';

CREATE TABLE maps.routing AS
SELECT 
	segmentkey, 
	startpoint, 
	endpoint, 
	segmentgeo::geometry as segmentgeom
FROM maps.osm_dk_20140101;

CREATE TABLE maps.routing2 AS
SELECT 
	segmentkey, 
	startpoint, 
	endpoint, 
	segmentgeo::geometry as segmentgeom
FROM maps.osm_dk_20140101 osm1
UNION
SELECT 
	segmentkey, 
	endpoint as startpoint, 
	startpoint as endpoint, 
	segmentgeo::geometry as segmentgeom
FROM maps.osm_dk_20140101
WHERE direction='BOTH';

SELECT pgr_createTopology('maps.routing', 0.001, 'segmentgeom', 'segmentkey', 'startpoint', 'endpoint');
SELECT pgr_createTopology('maps.routing2', 0.001, 'segmentgeom', 'segmentkey', 'startpoint', 'endpoint');

ALTER TABLE maps.routing
ADD COLUMN length float;

UPDATE maps.routing
SET length = maps.osm_dk_20140101.meters
FROM maps.osm_dk_20140101
WHERE maps.routing.segmentkey = maps.osm_dk_20140101.segmentkey;

ALTER TABLE maps.routing2
ADD COLUMN length float;

UPDATE maps.routing2
SET length = maps.osm_dk_20140101.meters
FROM maps.osm_dk_20140101
WHERE maps.routing2.segmentkey = maps.osm_dk_20140101.segmentkey;

CREATE TABLE embeddings.line (
	segmentkey bigint,
	emb_0 float,
	emb_1 float,
	emb_2 float,
	emb_3 float,
	emb_4 float,
	emb_5 float,
	emb_6 float,
	emb_7 float,
	emb_8 float,
	emb_9 float,
	emb_10 float,
	emb_11 float,
	emb_12 float,
	emb_13 float,
	emb_14 float,
	emb_15 float,
	emb_16 float,
	emb_17 float,
	emb_18 float,
	emb_19 float
);

CREATE UNIQUE INDEX embeddings_line_segmentkey_idx
    ON embeddings.line USING btree
    (segmentkey)
    TABLESPACE pg_default;
