CREATE OR REPLACE VIEW experiments.rmp10_test_roundabout AS
SELECT startpoint, endpoint, segmentkey, segmentgeo, meters
FROM maps.osm_dk_20140101 
JOIN (
SELECT array_agg(point) as points, ST_setSRID(ST_Extent(geom::geometry)::geometry, 4326) as box, ST_Union(geom::geometry), cid
FROM experiments.rmp10_interesting_nodes_aalborg_clustered4
WHERE cid = 72
GROUP BY cid
) temp
ON startpoint=ANY(points) OR endpoint=ANY(points)

CREATE VIEW experiments.rmp10_test_roundabout_shortest_end AS
SELECT tab.*
FROM (
	SELECT endpoint, min(meters)
	FROM experiments.rmp10_test_roundabout
	GROUP BY endpoint
) sub1
JOIN experiments.rmp10_test_roundabout tab
ON sub1.min = meters

CREATE OR REPLACE FUNCTION experiments.rmp10_ordinality(
	path integer[]
)
	RETURNS TABLE (
		n integer,
		node integer
	)
	LANGUAGE 'sql'
AS $$
	SELECT (row_number() OVER ())::integer as n, node FROM (
		SELECT unnest(path) as node
	) sub3;
$$;

CREATE OR REPLACE FUNCTION experiments.rmp10_truncate_cycle(
	endpoint integer, 
	path integer[]
)
	RETURNS integer[]
    LANGUAGE 'sql'
AS $$
SELECT array_agg(tab.node) 
FROM (
	SELECT n
	FROM experiments.rmp10_ordinality(path)
	WHERE node = endpoint
) sub
JOIN experiments.rmp10_ordinality(path) tab
ON tab.n >= sub.n;
$$;

WITH RECURSIVE search(startp, startgeo, endp, endgeo, path) AS (
	SELECT 
		startpoint as startp,
		ST_Startpoint(segmentgeo::geometry) as startgeo,
		endpoint as endp,
		ST_Endpoint(segmentgeo::geometry) as endgeo,
		ARRAY[startpoint] as path
	FROM (
		SELECT * 
		FROM experiments.rmp10_test_roundabout_shortest_start
		ORDER BY random()
		LIMIT 1
	) bla
	UNION ALL
	select 
		nxt.startpoint, 
		ST_Startpoint(nxt.segmentgeo::geometry), 
		nxt.endpoint, 
		ST_Endpoint(nxt.segmentgeo::geometry),
		prv.path || nxt.startpoint
	FROM experiments.rmp10_test_roundabout_shortest_start nxt
	JOIN search prv 
	ON nxt.startpoint = prv.endp
	AND nxt.endpoint != prv.endp
	AND NOT nxt.startpoint = ANY(path)
)
SELECT
	distinct startpoint, endpoint, segmentgeo, segmentkey, path
FROM (
	SELECT row_number() OVER () as n, startp, endp, experiments.rmp10_truncate_cycle(endp, path) as path
	FROM search
	ORDER BY n DESC
	LIMIT 1
) sub1
JOIN maps.osm_dk_20140101 osm
ON osm.startpoint = ANY(path) AND osm.endpoint = ANY(path)
