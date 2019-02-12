-- Create segment buffer table
DROP TABLE IF EXISTS experiments.rmp10_segment_buffers;

CREATE TABLE experiments.rmp10_segment_buffers AS
SELECT 
	ST_Buffer(segmentgeo, 30)::geometry as geom,
	segmentkey
FROM maps.osm_dk_20140101;

CREATE INDEX experiments_rmp10_segment_buffers_geom_index
    ON experiments.rmp10_segment_buffers USING gist
    (geom)
    WITH (FILLFACTOR=100)
    TABLESPACE pg_default;

CREATE INDEX experiments_rmp10_segment_buffers_key_index
    ON experiments.rmp10_segment_buffers USING btree
    (segmentkey)
    TABLESPACE pg_default;


-- Create traffic lights table
DROP TABLE IF EXISTS experiments.rmp10_traffic_lights;

CREATE TABLE experiments.rmp10_traffic_lights AS
SELECT
	ST_Transform(way, 4326) as way
FROM experiments.rmp10_planet_osm_point
WHERE highway='traffic_signals';

CREATE INDEX experiments_rmp10_traffic_lights_index
    ON experiments.rmp10_traffic_lights USING gist
    (way)
    WITH (FILLFACTOR=100)
    TABLESPACE pg_default;


-- Create intersection table
DROP TABLE IF EXISTS experiments.rmp10_intersections;

CREATE TABLE experiments.rmp10_intersections AS
SELECT 
	osm.segmentkey,
	CASE WHEN traffic_lights.segmentkey is NULL
		 THEN False
		 ELSE True
	END as intersection
FROM maps.osm_dk_20140101 as osm
FULL OUTER JOIN (
	SELECT
		DISTINCT segmentkey
	FROM experiments.rmp10_segment_buffers
	JOIN experiments.rmp10_traffic_lights
	ON ST_Contains(geom, way)
) as traffic_lights
ON traffic_lights.segmentkey = osm.segmentkey;

CREATE INDEX experiments_rmp10_intersections_flag_index
    ON experiments.rmp10_intersections USING btree
    (segmentkey)
    TABLESPACE pg_default    WHERE intersection;

CREATE INDEX experiments_rmp10_intersections_key_index
    ON experiments.rmp10_intersections USING btree
    (segmentkey)
    TABLESPACE pg_default;
