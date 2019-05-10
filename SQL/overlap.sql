CREATE TABLE experiments.rmp10_overlapping_segments AS
SELECT segment, count(segment)
FROM (
	SELECT
		CASE WHEN (ss1.startseg = ss2.startseg) 
			 OR (ss1.startseg = ss2.endseg) 
			 THEN ss1.startseg
			 ELSE ss1.endseg
		END AS segment
	FROM experiments.rmp10_all_supersegments ss1
	JOIN experiments.rmp10_all_supersegments ss2
	ON (ss1.startseg = ss2.startseg AND ss1.startpoint <> ss2.startpoint)
	OR (ss1.startseg = ss2.endseg   AND ss1.startpoint <> ss2.endpoint)
	OR (ss1.endseg 	 = ss2.startseg AND ss1.endpoint   <> ss2.startpoint)
	OR (ss1.endseg   = ss2.endseg   AND ss1.endpoint   <> ss2.endpoint)
) sub
GROUP BY segment

INSERT INTO experiments.rmp10_osm_dk_20140101_overlaps (
	segmentkey, segmentgeo, startpoint, endpoint, origin
)
WITH seg AS (
	SELECT osm.* 
	FROM maps.osm_dk_20140101 osm
	JOIN experiments.rmp10_overlapping_segments ss
	ON osm.segmentkey = ss.segment
)
SELECT 
	nextval('experiments.rmp10_segmentkey_seq') as segmentkey, 
	geo as segmentgeo, 
	startpoint,
	nextval('experiments.rmp10_point_seq') as endpoint,
	origin
FROM (
	SELECT 
		ST_LineSubstring(segmentgeo::geometry, 0, 0.5)::geography as geo,
		segmentkey as origin,
		startpoint
	FROM seg
	/*UNION
	SELECT 
		ST_LineSubstring(segmentgeo::geometry, 0.5, 1)::geography as geo,
		segmentkey as origin,
		null as startpoint,
		endpoint
	FROM seg*/
) sub
