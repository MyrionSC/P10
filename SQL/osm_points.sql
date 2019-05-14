ALTER TABLE experiments.rmp10_osm_points
ADD COLUMN degree integer;

UPDATE experiments.rmp10_osm_points op
SET degree = sub2.degree
FROM (
	SELECT point, count(point) as degree
	FROM (
		SELECT startpoint as point
		FROM maps.osm_dk_20140101 osm1
		UNION ALL
		SELECT endpoint as point
		FROM maps.osm_dk_20140101 osm2
	) sub
	GROUP BY point
) sub2
WHERE op.point = sub2.point;

ALTER TABLE experiments.rmp10_traffic_lights_temp
ADD COLUMN lights integer[] DEFAULT ARRAY[]::integer[];
UPDATE experiments.rmp10_traffic_lights_temp tlst
SET lights = tlss
FROM (
	WITH osms AS (
		SELECT cid, id, type 
		FROM experiments.rmp10_traffic_lights_temp
		WHERE type = 'OSM'
	), tls AS (
		SELECT cid, id, type
		FROM experiments.rmp10_traffic_lights_temp
		WHERE type = 'TL'
	)
	SELECT osms.cid, osms.type, osms.id, array_agg(tls.id) as tlss
	FROM osms
	JOIN tls
	ON tls.cid = osms.cid
	GROUP BY osms.id, osms.cid, osms.type
) sub
WHERE sub.id = tlst.id AND tlst.type = 'OSM'

ALTER TABLE experiments.rmp10_osm_points
ADD COLUMN lights integer[] DEFAULT ARRAY[]::integer[];
UPDATE experiments.rmp10_osm_points
SET lights = sub.lights
FROM experiments.rmp10_traffic_lights_temp sub
WHERE type = 'OSM' AND id = point