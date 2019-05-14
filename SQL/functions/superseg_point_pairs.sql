CREATE FUNCTION superseg_point_pairs(segments integer[])
RETURNS integer[][]
LANGUAGE 'sql'
AS $$
	WITH segs as (
		SELECT unnest(segments) as segment
	)
	SELECT array_agg(points)
	FROM (
		SELECT ARRAY[startpoint, endpoint] as points
		FROM segs
		JOIN maps.osm_dk_20140101 osm
		ON segs.segment = osm.segmentkey
	) sub
$$