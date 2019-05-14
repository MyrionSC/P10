CREATE TABLE experiments.rmp10_test AS
WITH zip_geog AS (
	SELECT ST_Union(geog::geometry) as geom
	FROM regions.dk_zip
	WHERE zip_start >= 9000
), trips AS (
	SELECT distinct trip_id
	FROM mapmatched_data.viterbi_match_osm_dk_20140101 vit
	JOIN maps.osm_dk_20140101 osm
	ON osm.segmentkey = vit.segmentkey
	JOIN zip_geog
	ON ST_intersects(geom, osm.segmentgeo::geometry)
)
SELECT vit.* 
FROM mapmatched_data.viterbi_match_osm_dk_20140101 vit
JOIN trips
ON trips.trip_id = vit.trip_id

WITH trip_ids AS (
	SELECT distinct vit.trip_id
	FROM mapmatched_data.viterbi_match_osm_dk_20140101 vit
	WHERE NOT EXISTS (
		SELECT
		FROM experiments.rmp10_test tt
		WHERE vit.trip_id = tt.trip_id
	)
)
INSERT INTO experiments.rmp10_test
SELECT vit.*
FROM mapmatched_data.viterbi_match_osm_dk_20140101 vit
JOIN (
	SELECT * 
	FROM trip_ids
	ORDER BY random()
	LIMIT 69468
) tid
ON tid.trip_id = vit.trip_id;

CREATE TABLE experiments.rmp10_training AS
SELECT * 
FROM mapmatched_data.viterbi_match_osm_dk_20140101 vit
WHERE NOT EXISTS (
	SELECT
	FROM experiments.rmp10_test tt
	WHERE vit.trip_id = tt.trip_id
);

CREATE TABLE experiments.rmp10_test_supersegs AS
SELECT os.* 
FROM experiments.rmp10_viterbi_match_osm_dk_20140101_overlap os
WHERE NOT EXISTS (
	SELECT
	FROM experiments.rmp10_training tt
	WHERE tt.trip_id = os.trip_id
);

CREATE TABLE experiments.rmp10_test_supersegs AS
SELECT os.* 
FROM experiments.rmp10_viterbi_match_osm_dk_20140101_overlap os
WHERE NOT EXISTS (
	SELECT
	FROM experiments.rmp10_training tt
	WHERE tt.trip_id = os.trip_id
);

CREATE TABLE experiments.rmp10_training_supersegs AS
SELECT os.* 
FROM experiments.rmp10_viterbi_match_osm_dk_20140101_overlap os
WHERE EXISTS (
	SELECT
	FROM experiments.rmp10_training tt
	WHERE tt.trip_id = os.trip_id
);

CREATE INDEX rmp10_training_ixd_datekey_viterbi
    ON experiments.rmp10_training_supersegs USING btree
    (datekey)
    TABLESPACE pg_default;

CREATE INDEX rmp10_training_trip_with_segments_multi_index
    ON experiments.rmp10_training_supersegs USING btree
    (trip_id, trip_segmentno)
    TABLESPACE pg_default;

CREATE INDEX rmp10_training_supersegs_segmentkey_index
    ON experiments.rmp10_training_supersegs USING btree
    (segmentkey DESC NULLS LAST)
    TABLESPACE pg_default;

CREATE INDEX rmp10_training_supersegs_segmentkey_index_asc
    ON experiments.rmp10_training_supersegs USING btree
    (segmentkey ASC NULLS LAST)
    TABLESPACE pg_default;

CREATE INDEX rmp10_training_supersegs_trip_id_index
    ON experiments.rmp10_training_supersegs USING btree
    (trip_id)
    TABLESPACE pg_default;

CREATE INDEX rmp10_test_ixd_datekey_viterbi
    ON experiments.rmp10_test_supersegs USING btree
    (datekey)
    TABLESPACE pg_default;

CREATE INDEX rmp10_test_trip_with_segments_multi_index
    ON experiments.rmp10_test_supersegs USING btree
    (trip_id, trip_segmentno)
    TABLESPACE pg_default;

CREATE INDEX rmp10_test_supersegs_segmentkey_index
    ON experiments.rmp10_test_supersegs USING btree
    (segmentkey DESC NULLS LAST)
    TABLESPACE pg_default;

CREATE INDEX rmp10_test_supersegs_segmentkey_index_asc
    ON experiments.rmp10_test_supersegs USING btree
    (segmentkey ASC NULLS LAST)
    TABLESPACE pg_default;

CREATE INDEX rmp10_test_supersegs_trip_id_index
    ON experiments.rmp10_test_supersegs USING btree
    (trip_id)
    TABLESPACE pg_default;