CREATE OR REPLACE FUNCTION rmp10_get_geo(
	segs integer[]
)
	RETURNS geometry
	LANGUAGE 'sql'
AS $$
	select st_union(segmentgeo::geometry)
	from (
		SELECT segmentkey, segmentgeo FROM maps.osm_dk_20140101
		UNION
		SELECT segmentkey, segmentgeo FROM experiments.rmp10_osm_dk_20140101_overlaps
	) sub
	where segmentkey=any(segs)
$$;


