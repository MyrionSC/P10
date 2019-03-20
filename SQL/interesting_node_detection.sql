-- Identify all nodes and node-degrees
CREATE VIEW experiments.rmp10_all_points AS
SELECT point, geom, count(*) as degree
FROM (
	SELECT point, geom
	FROM (SELECT startpoint as point, ST_Startpoint(segmentgeo::geometry)::geography as geom FROM maps.osm_dk_20140101) sp 
	UNION ALL
	SELECT point, geom
	FROM (SELECT endpoint as point, ST_Endpoint(segmentgeo::geometry)::geography as geom FROM maps.osm_dk_20140101) ep
) points
GROUP BY point, geom;

-- Identify all interestings nodes (t-junctions, junctions, links, roundabouts etc.) by filtering by a node degree of 3 or higher
CREATE TABLE experiments.rmp10_interesting_nodes AS
SELECT *
FROM experiments.rmp10_all_points
WHERE degree >= 3;

-- Identify all points where the road category switches
INSERT INTO experiments.rmp10_interesting_nodes (point, geom, degree)
SELECT point, geom, degree
FROM experiments.rmp10_all_points
JOIN (
	SELECT DISTINCT shared 
	FROM (
		SELECT 
			osm1.segmentkey, 
			osm2.segmentkey,
			osm1.category,
			osm2.category,
			CASE WHEN osm1.endpoint=ANY(ARRAY[osm2.startpoint, osm2.endpoint])
				 THEN osm1.endpoint 
				 ELSE osm1.startpoint
			END as shared
		FROM maps.osm_dk_20140101 osm1
		JOIN maps.osm_dk_20140101 osm2
		ON osm1.segmentkey <> osm2.segmentkey
		AND (osm1.endpoint=ANY(ARRAY[osm2.startpoint, osm2.endpoint])
		OR osm1.startpoint=ANY(ARRAY[osm2.startpoint, osm2.endpoint]))
		AND osm1.category <> osm2.category
	) d
) p
ON p.shared = point
WHERE degree < 3;

-- Identify all roads that have been driven on as well as the number of traversals of each road
CREATE TABLE experiments.rmp10_osm_dk_20140101_driven AS
SELECT osm.*, num_traversals
FROM (
	SELECT segmentkey, count(*) as num_traversals
	FROM mapmatched_data.viterbi_match_osm_dk_20140101
	GROUP BY segmentkey
) vit
JOIN maps.osm_dk_20140101 osm
ON osm.segmentkey = vit.segmentkey;

-- Identify all nodes that have been driven over
CREATE VIEW experiments.rmp10_driven_points_segments AS
SELECT point, geom, array_agg(segmentkey) as segments, max(num_traversals) as max_trips
FROM (
	SELECT point, geom, segmentkey, num_traversals
	FROM (SELECT startpoint as point, ST_Startpoint(segmentgeo::geometry)::geography as geom, segmentkey, num_traversals FROM experiments.rmp10_osm_dk_20140101_driven) sp 
	UNION ALL
	SELECT point, geom, segmentkey, num_traversals
	FROM (SELECT endpoint as point, ST_Endpoint(segmentgeo::geometry)::geography as geom, segmentkey, num_traversals FROM experiments.rmp10_osm_dk_20140101_driven) ep
) points
GROUP BY point, geom;

-- Identify all interesting nodes that have been driven over
CREATE TABLE experiments.rmp10_driven_interesting_nodes AS
SELECT nod.*, pnts.degree as driven_degree, pnts.max_trips, pnts.segments
FROM experiments.rmp10_driven_points_segments pnts
JOIN experiments.rmp10_interesting_nodes nod
ON pnts.point = nod.point;
