CREATE SEQUENCE experiments.rmp10_segmentkey_seq 
INCREMENT BY 2
START 751041;

INSERT INTO experiments.rmp10_osm_dk_20140101_overlaps (
	segmentkey, segmentgeo, startpoint, endpoint, origin
)
WITH seg AS (
	SELECT osm.* 
	FROM maps.osm_dk_20140101 osm
	JOIN experiments.rmp10_overlapping_segments ss
	ON osm.segmentkey = ss.segment
)
SELECT 
	nextval('experiments.rmp10_segmentkey_seq') as segmentkey, 
	geo as segmentgeo, 
	startpoint,
	endpoint,
	origin
FROM (
	SELECT 
		ST_LineSubstring(segmentgeo::geometry, 0, 0.5)::geography as geo,
		segmentkey as origin,
		startpoint,
		null as endpoint
	FROM seg
	UNION
	SELECT 
		ST_LineSubstring(segmentgeo::geometry, 0.5, 1)::geography as geo,
		segmentkey as origin,
		null as startpoint,
		endpoint
	FROM seg
) sub

CREATE SEQUENCE experiments.rmp10_point_seq
START 650600;

CREATE INDEX rmp10_osm_dk_20140101_category_idx
    ON experiments.rmp10_osm_dk_20140101_overlaps USING btree
    (category)
    WITH (FILLFACTOR=100)
    TABLESPACE pg_default;

CREATE INDEX rmp10_osm_dk_20140101_categoryid_idx
    ON experiments.rmp10_osm_dk_20140101_overlaps USING btree
    (categoryid)
    WITH (FILLFACTOR=100)
    TABLESPACE pg_default;

CREATE INDEX rmp10_osm_dk_20140101_categoryid_idx1
    ON experiments.rmp10_osm_dk_20140101_overlaps USING btree
    (categoryid)
    TABLESPACE pg_default;

CREATE INDEX rmp10_osm_dk_20140101_direction_idx
    ON experiments.rmp10_osm_dk_20140101_overlaps USING btree
    (direction)
    WITH (FILLFACTOR=100)
    TABLESPACE pg_default;

CREATE INDEX rmp10_osm_dk_20140101_endpoint_idx
    ON experiments.rmp10_osm_dk_20140101_overlaps USING btree
    (endpoint)
    WITH (FILLFACTOR=100)
    TABLESPACE pg_default;

CREATE INDEX rmp10_osm_dk_20140101_segangle_idx
    ON experiments.rmp10_osm_dk_20140101_overlaps USING btree
    (segangle)
    WITH (FILLFACTOR=100)
    TABLESPACE pg_default;

CREATE INDEX rmp10_osm_dk_20140101_segmentgeo_25832_index
    ON experiments.rmp10_osm_dk_20140101_overlaps USING btree
    (st_transform(segmentgeo::geometry, 25832))
    TABLESPACE pg_default;

CREATE INDEX rmp10_osm_dk_20140101_segmentgeo_end_index
    ON experiments.rmp10_osm_dk_20140101_overlaps USING btree
    (st_endpoint(st_transform(segmentgeo::geometry, 25832)))
    TABLESPACE pg_default;

CREATE INDEX rmp10_osm_dk_20140101_segmentgeo_idx
    ON experiments.rmp10_osm_dk_20140101_overlaps USING gist
    (segmentgeo)
    WITH (FILLFACTOR=100)
    TABLESPACE pg_default;

CREATE INDEX rmp10_osm_dk_20140101_segmentkey_categoryid_category_direction_me_idx
    ON experiments.rmp10_osm_dk_20140101_overlaps USING btree
    (segmentkey, categoryid, category, direction, meters)
    TABLESPACE pg_default;

CREATE INDEX rmp10_osm_dk_20140101_segmentkey_idx
    ON experiments.rmp10_osm_dk_20140101_overlaps USING btree
    (segmentkey)
    TABLESPACE pg_default;

CREATE INDEX rmp10_osm_dk_20140101_speedlimit_backward_idx
    ON experiments.rmp10_osm_dk_20140101_overlaps USING btree
    (speedlimit_backward)
    WITH (FILLFACTOR=100)
    TABLESPACE pg_default;

CREATE INDEX rmp10_osm_dk_20140101_speedlimit_backward_idx1
    ON experiments.rmp10_osm_dk_20140101_overlaps USING btree
    (speedlimit_backward)
    TABLESPACE pg_default;

CREATE INDEX rmp10_osm_dk_20140101_speedlimit_forward_idx
    ON experiments.rmp10_osm_dk_20140101_overlaps USING btree
    (speedlimit_forward)
    WITH (FILLFACTOR=100)
    TABLESPACE pg_default;

CREATE INDEX rmp10_osm_dk_20140101_speedlimit_forward_idx1
    ON experiments.rmp10_osm_dk_20140101_overlaps USING btree
    (speedlimit_forward)
    TABLESPACE pg_default;

CREATE INDEX rmp10_osm_dk_20140101_start_index
    ON experiments.rmp10_osm_dk_20140101_overlaps USING btree
    (st_startpoint(st_transform(segmentgeo::geometry, 25832)))
    TABLESPACE pg_default;

CREATE INDEX rmp10_osm_dk_20140101_startpoint_idx
    ON experiments.rmp10_osm_dk_20140101_overlaps USING btree
    (startpoint)
    WITH (FILLFACTOR=100)
    TABLESPACE pg_default;