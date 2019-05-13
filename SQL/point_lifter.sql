ALTER TABLE experiments.rmp10_osm_dk_20140101_overlaps_points
ADD COLUMN height double precision;

UPDATE experiments.rmp10_osm_dk_20140101_overlaps_points op
SET height = h
FROM (
	SELECT p.point, ST_NearestValue(r.rast, p.geo::geometry) as h
	FROM experiments.bcj_heightmapbridge r
	JOIN experiments.rmp10_osm_dk_20140101_overlaps_points p
	ON ST_Intersects(p.geo::geometry, r.rast)
) sub
WHERE sub.point = op.point;
