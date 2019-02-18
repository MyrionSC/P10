-- Table: maps.osm_dk_20140101

-- DROP TABLE maps.osm_dk_20140101;

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

-- Index: osm_dk_20140101_category_idx

-- DROP INDEX maps.osm_dk_20140101_category_idx;

CREATE INDEX osm_dk_20140101_category_idx
    ON maps.osm_dk_20140101 USING btree
    (category)
    WITH (FILLFACTOR=100)
    TABLESPACE pg_default;

-- Index: osm_dk_20140101_categoryid_idx

-- DROP INDEX maps.osm_dk_20140101_categoryid_idx;

CREATE INDEX osm_dk_20140101_categoryid_idx
    ON maps.osm_dk_20140101 USING btree
    (categoryid)
    WITH (FILLFACTOR=100)
    TABLESPACE pg_default;

-- Index: osm_dk_20140101_categoryid_idx1

-- DROP INDEX maps.osm_dk_20140101_categoryid_idx1;

CREATE INDEX osm_dk_20140101_categoryid_idx1
    ON maps.osm_dk_20140101 USING btree
    (categoryid)
    TABLESPACE pg_default;

-- Index: osm_dk_20140101_direction_idx

-- DROP INDEX maps.osm_dk_20140101_direction_idx;

CREATE INDEX osm_dk_20140101_direction_idx
    ON maps.osm_dk_20140101 USING btree
    (direction)
    WITH (FILLFACTOR=100)
    TABLESPACE pg_default;

-- Index: osm_dk_20140101_endpoint_idx

-- DROP INDEX maps.osm_dk_20140101_endpoint_idx;

CREATE INDEX osm_dk_20140101_endpoint_idx
    ON maps.osm_dk_20140101 USING btree
    (endpoint)
    WITH (FILLFACTOR=100)
    TABLESPACE pg_default;

-- Index: osm_dk_20140101_segmentgeo_25832_index

-- DROP INDEX maps.osm_dk_20140101_segmentgeo_25832_index;

CREATE INDEX osm_dk_20140101_segmentgeo_25832_index
    ON maps.osm_dk_20140101 USING btree
    (st_transform(segmentgeo::geometry, 25832))
    TABLESPACE pg_default;

-- Index: osm_dk_20140101_segmentgeo_end_index

-- DROP INDEX maps.osm_dk_20140101_segmentgeo_end_index;

CREATE INDEX osm_dk_20140101_segmentgeo_end_index
    ON maps.osm_dk_20140101 USING btree
    (st_endpoint(st_transform(segmentgeo::geometry, 25832)))
    TABLESPACE pg_default;

-- Index: osm_dk_20140101_segmentgeo_idx

-- DROP INDEX maps.osm_dk_20140101_segmentgeo_idx;

CREATE INDEX osm_dk_20140101_segmentgeo_idx
    ON maps.osm_dk_20140101 USING gist
    (segmentgeo)
    WITH (FILLFACTOR=100)
    TABLESPACE pg_default;

-- Index: osm_dk_20140101_segmentkey_categoryid_category_direction_me_idx

-- DROP INDEX maps.osm_dk_20140101_segmentkey_categoryid_category_direction_me_idx;

CREATE INDEX osm_dk_20140101_segmentkey_categoryid_category_direction_me_idx
    ON maps.osm_dk_20140101 USING btree
    (segmentkey, categoryid, category, direction, meters)
    TABLESPACE pg_default;

-- Index: osm_dk_20140101_segmentkey_idx

-- DROP INDEX maps.osm_dk_20140101_segmentkey_idx;

CREATE INDEX osm_dk_20140101_segmentkey_idx
    ON maps.osm_dk_20140101 USING btree
    (segmentkey)
    TABLESPACE pg_default;

-- Index: osm_dk_20140101_speedlimit_backward_idx

-- DROP INDEX maps.osm_dk_20140101_speedlimit_backward_idx;

CREATE INDEX osm_dk_20140101_speedlimit_backward_idx
    ON maps.osm_dk_20140101 USING btree
    (speedlimit_backward)
    WITH (FILLFACTOR=100)
    TABLESPACE pg_default;

-- Index: osm_dk_20140101_speedlimit_backward_idx1

-- DROP INDEX maps.osm_dk_20140101_speedlimit_backward_idx1;

CREATE INDEX osm_dk_20140101_speedlimit_backward_idx1
    ON maps.osm_dk_20140101 USING btree
    (speedlimit_backward)
    TABLESPACE pg_default;

-- Index: osm_dk_20140101_speedlimit_forward_idx

-- DROP INDEX maps.osm_dk_20140101_speedlimit_forward_idx;

CREATE INDEX osm_dk_20140101_speedlimit_forward_idx
    ON maps.osm_dk_20140101 USING btree
    (speedlimit_forward)
    WITH (FILLFACTOR=100)
    TABLESPACE pg_default;

-- Index: osm_dk_20140101_speedlimit_forward_idx1

-- DROP INDEX maps.osm_dk_20140101_speedlimit_forward_idx1;

CREATE INDEX osm_dk_20140101_speedlimit_forward_idx1
    ON maps.osm_dk_20140101 USING btree
    (speedlimit_forward)
    TABLESPACE pg_default;

-- Index: osm_dk_20140101_start_index

-- DROP INDEX maps.osm_dk_20140101_start_index;

CREATE INDEX osm_dk_20140101_start_index
    ON maps.osm_dk_20140101 USING btree
    (st_startpoint(st_transform(segmentgeo::geometry, 25832)))
    TABLESPACE pg_default;

-- Index: osm_dk_20140101_startpoint_idx

-- DROP INDEX maps.osm_dk_20140101_startpoint_idx;

CREATE INDEX osm_dk_20140101_startpoint_idx
    ON maps.osm_dk_20140101 USING btree
    (startpoint)
    WITH (FILLFACTOR=100)
    TABLESPACE pg_default;