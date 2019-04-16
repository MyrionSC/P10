DROP TABLE IF EXISTS experiments.rmp10_driven_supersegments_2len_mt10_driven;

CREATE TABLE experiments.rmp10_driven_supersegments_2len_mt10_driven (
	superseg_id BIGSERIAL,
	segments integer[]
);

INSERT INTO experiments.rmp10_driven_supersegments_2len_mt10_driven (segments)
SELECT ARRAY[osm1.segmentkey, osm2.segmentkey] as segments
FROM experiments.rmp10_osm_dk_20140101_driven osm1
JOIN experiments.rmp10_osm_dk_20140101_driven osm2
ON
	osm1.num_traversals>=10 AND
	osm2.num_traversals>=10 AND
	(osm1.endpoint = ANY(ARRAY[osm2.startpoint, osm2.endpoint]) OR
	osm1.startpoint = ANY(ARRAY[osm2.startpoint, osm2.endpoint]))

