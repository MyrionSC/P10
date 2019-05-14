CREATE FUNCTION rmp10_meters_superseg(segments integer[])
RETURNS real
LANGUAGE 'sql'
AS $$
SELECT sum(meters)
FROM (
	SELECT unnest(segments) as segmentkey
) sub
JOIN maps.osm_dk_20140101 osm
ON sub.segmentkey = osm.segmentkey
$$