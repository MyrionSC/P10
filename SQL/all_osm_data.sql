SELECT distinct(unnest(segments)) as segmentkey
INTO experiments.rmp10_all_supersegments_unnested
FROM experiments.rmp10_all_supersegments;

CREATE INDEX rmp10_all_supersegments_unnested_segmentkey_idx
ON experiments.rmp10_all_supersegments_unnested
USING btree(segmentkey);

DROP TABLE IF EXISTS experiments.rmp10_all_osm_data;

CREATE TABLE experiments.rmp10_all_osm_data
AS TABLE experiments.rmp10_all_supersegments;

ALTER TABLE experiments.rmp10_all_osm_data
ADD COLUMN segmentkey integer;

INSERT INTO experiments.rmp10_all_osm_data
SELECT
	ARRAY[segmentkey] as segments,
	null as startseg,
	null as endseg,
	startpoint,
	endpoint,
	ARRAY[startpoint, endpoint] as points,
	null as num_traversals,
	'STRAIGHT' as direction,
	ARRAY[category] as categories,
	null as lights,
	False as traffic_lights,
	'Segment' as type,
	null as height_difference,
	0.0 as cat_speed_difference,
	null as superseg_id,
	origin,
	null as startdir,
	null as endir,
	meters as meters,
	segmentkey
FROM experiments.rmp10_osm_dk_20140101_overlaps ol
WHERE NOT EXISTS (
	SELECT
	FROM experiments.rmp10_all_supersegments_unnested atsids
	WHERE ol.segmentkey = atsids.segmentkey
);
	
	
	

