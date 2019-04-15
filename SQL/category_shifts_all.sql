DROP TABLE IF EXISTS experiments.rmp10_category_change_all;
CREATE TABLE experiments.rmp10_category_change_all (
	superseg_id BIGSERIAL,
	segments integer[],
	categories functionality.osm_categories[]
);

INSERT INTO experiments.rmp10_category_change_all (segments, categories)
SELECT ARRAY[osm1.segmentkey, osm2.segmentkey] as segments, ARRAY[osm1.category, osm2.category] as categories
FROM maps.osm_dk_20140101 osm1
JOIN maps.osm_dk_20140101 osm2
ON CASE WHEN osm1.direction = 'FORWARD' AND osm2.direction = 'FORWARD' THEN osm1.endpoint = osm2.startpoint
	    WHEN osm1.direction = 'BOTH' AND osm2.direction = 'FORWARD' THEN osm2.startpoint=ANY(ARRAY[osm1.startpoint, osm1.endpoint])
        WHEN osm1.direction = 'FORWARD' AND osm2.direction = 'BOTH'	THEN osm1.endpoint=ANY(ARRAY[osm2.startpoint, osm2.endpoint])
	    WHEN osm1.direction = 'BOTH' AND osm2.direction = 'BOTH' THEN (osm1.startpoint=ANY(ARRAY[osm2.startpoint, osm2.endpoint]) OR osm1.endpoint=ANY(ARRAY[osm2.startpoint, osm2.endpoint]))
		END
AND osm1.category <> osm2.category;