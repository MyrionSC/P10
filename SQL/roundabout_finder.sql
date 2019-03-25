-- Expand an array and index the elements
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

-- Remove all elements of an array before a given element
-- Used to truncate the cycles and ignore the segments before the search entered the cycle
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

-- Locate roundabouts in a cluster
CREATE OR REPLACE FUNCTION experiments.rmp10_roundabout_locater (cluster_id integer)
RETURNS integer[]
LANGUAGE 'sql'
AS $$
-- Do a depth first search where the selected next node is the closest on the the current.
WITH RECURSIVE search(startp, startgeo, endp, endgeo, path) AS (
	-- Truncate sub-graph to only include the shortest out-edges from each node.
	WITH rmp10_test_roundabout_shortest_start AS (
		-- Calculate the subgraph inside a cluster based on a cluster_id
		WITH rmp10_test_roundabout AS (
			-- Get all segments intersecting the points in a cluster
			SELECT 
				osm_dk_20140101.startpoint, 
				osm_dk_20140101.endpoint, 
				osm_dk_20140101.segmentkey, 
				osm_dk_20140101.segmentgeo, 
				osm_dk_20140101.meters 
			FROM maps.osm_dk_20140101 
			JOIN (
				-- Get all points in a cluster
				SELECT 
					array_agg(rmp10_interesting_nodes_clustered.point) AS points,
				FROM experiments.rmp10_interesting_nodes_clustered
				WHERE rmp10_interesting_nodes_clustered.cid = cluster_id
			) temp 
			ON osm_dk_20140101.startpoint = ANY (temp.points)
			OR osm_dk_20140101.endpoint = ANY (temp.points)
		)
		-- Select only the edges with the shortest distance
		SELECT 
			tab.startpoint, 
			tab.endpoint,
			tab.segmentgeo
		FROM (
			-- Calculate the shortest distance from a point and it's outgoing neighbours
			SELECT 
				sub2.startpoint, 
				min(sub2.meters) AS min 
			FROM rmp10_test_roundabout sub2 
			GROUP BY sub2.startpoint
		) sub1 
		JOIN rmp10_test_roundabout tab
		ON sub1.startpoint = tab.startpoint
		AND sub1.min = tab.meters
	)
	-- Initial step: Select random startpoint
	SELECT 
		startpoint as startp,
		endpoint as endp,
		ARRAY[startpoint] as path
	FROM (
		-- Select a random point
		SELECT * 
		FROM rmp10_test_roundabout_shortest_start
		ORDER BY random()
		LIMIT 1
	) bla
	-- Recursive step: Depth first search
	UNION ALL
	select 
		nxt.startpoint,
		nxt.endpoint,
		prv.path || nxt.startpoint -- Append current point to path
	FROM rmp10_test_roundabout_shortest_start nxt
	JOIN search prv 
	ON nxt.startpoint = prv.endp -- Next segment must be in sequence with previous
	AND nxt.endpoint != prv.endp -- Disregard self loops
	AND prv.startp != nxt.endpoint -- Disregard cycles of length 2
	AND NOT nxt.startpoint = ANY(path) -- Terminate when encountering a cycle
)
-- Select the calculated path from the last recursive step (when it encountered a cycle)
SELECT
	distinct path
FROM (
	-- Select the last step of the search
	SELECT row_number() OVER () as n, startp, endp, experiments.rmp10_truncate_cycle(endp, path) as path
	FROM search
	ORDER BY n DESC
	LIMIT 1
) sub1
LIMIT 1; -- Ensure only 1 result is returned
$$;

-- Get segment information about the cycles identified by the search
SELECT cid, ST_Union(segmentgeo::geometry)::geography FROM (
	-- Get the non-empty cycles
	SELECT * FROM (
		-- Calculate cycles for all clusters
		SELECT cid, experiments.rmp10_roundabout_locater(cid) as cycles
		FROM (
			-- Select all cluster ids
			SELECT DISTINCT cid 
			FROM experiments.rmp10_interesting_nodes_clustered
			WHERE cid IS NOT NULL -- Disregard unclustered points
		) sub
	) sub2
	WHERE cycles IS NOT NULL -- Disregard clusters without cycles
) sub3 
JOIN maps.osm_dk_20140101 osm
ON osm.startpoint = ANY(cycles)
AND osm.endpoint = ANY(cycles)
AND array_length(cycles, 1) > 2 -- Disregard self-loops
GROUP BY cid
