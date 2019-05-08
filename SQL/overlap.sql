SELECT ss1.segments, ss2.segments
FROM (SELECT segments, startpoint, endpoint FROM experiments.rmp10_intersection_supersegments LIMIT 100) ss1
JOIN experiments.rmp10_intersection_supersegments ss2
ON (ss1.segments[1] = ss2.segments[1] AND ss1.startpoint <> ss2.startpoint)
OR (ss1.segments[1] = ss2.segments[array_length(ss2.segments, 1)] AND ss1.startpoint <> ss2.endpoint)
OR (ss1.segments[array_length(ss1.segments, 1)] = ss2.segments[1] AND ss1.endpoint <> ss2.startpoint)
OR (ss1.segments[array_length(ss1.segments, 1)] = ss2.segments[array_length(ss2.segments, 1)] AND ss1.endpoint <> ss2.endpoint)

SELECT distinct segmentkey
FROM maps.osm_dk_20140101 as seg
LEFT JOIN (SELECT * FROM experiments.rmp10_intersection_supersegments LIMIT 1) ss1
ON segmentkey = ANY(ss1.segments)
LEFT JOIN experiments.rmp10_intersection_supersegments ss2
ON ss1.segments <> ss2.segments
AND NOT(ss1.startpoint = ss2.endpoint AND ss1.endpoint = ss2.startpoint)
AND segmentkey = ANY(ss2.segments)

WITH overlapper AS (
	SELECT 
		ss1.segments as segments1, ss1.startpoint as startpoint1, ss1.endpoint as endpoint1, 
		ss2.segments as segments2, ss2.startpoint as startpoint2, ss2.endpoint as endpoint2, 
		array_intersect(ss1.segments, ss2.segments) as overlap
	FROM (SELECT segments, startpoint, endpoint FROM experiments.rmp10_intersection_supersegments LIMIT 10) ss1
	JOIN experiments.rmp10_intersection_supersegments ss2
	ON ss1.startpoint <> ss2.endpoint AND ss1.endpoint <> ss2.startpoint
	AND array_length(array_intersect(ss1.segments, ss2.segments), 1) > 0
	--LIMIT 10
)
SELECT 
	*
FROM overlapper
WHERE CASE WHEN segments1[1] = ANY(overlap)
		 THEN CASE WHEN segments2[1] = ANY(overlap)
		 		   THEN startpoint1 <> startpoint2
				   ELSE startpoint1 <> endpoint2 END
		 ELSE CASE WHEN segments2[1] = ANY(overlap)
		 		   THEN endpoint1 <> startpoint2
				   ELSE endpoint1 <> endpoint2 END
	 END
