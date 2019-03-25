CREATE OR REPLACE VIEW experiments.rmp10_aalborg_intersection1 AS
SELECT segs.segmentkey,
    segs.segmentgeo,
    segs.startpoint,
    segs.endpoint,
    pts.geom,
    CASE WHEN (segs.startpoint = ANY (ARRAY[23060, 23061, 359483, 422928])) 
         AND (segs.endpoint = ANY (ARRAY[23060, 23061, 359483, 422928])) 
         THEN true
         ELSE false
    END AS internal
FROM experiments.rmp10_aalborg_points pts
JOIN experiments.rmp10_aalborg_routing segs 
ON segs.startpoint = pts.point 
OR segs.endpoint = pts.point
WHERE pts.point = ANY (ARRAY[23060, 23061, 359483, 422928]);

CREATE OR REPLACE VIEW experiments.rmp10_intersection1_right_swings AS
SELECT 
	ARRAY[x1.segmentkey, x2.segmentkey] as segments, 
	ARRAY[x1.startpoint, x2.startpoint, x2.endpoint] as points,
	ARRAY[x1.segmentgeo, x2.segmentgeo] as geoms,
	ST_Union(x1.segmentgeo, x2.segmentgeo) as supersegmentgeom,
	experiments.circ(degrees(
		ST_Azimuth(ST_Startpoint(x1.segmentgeo), ST_Endpoint(x1.segmentgeo))
		- 
		ST_Azimuth(ST_Startpoint(x2.segmentgeo), ST_Endpoint(x2.segmentgeo)) 
	)) as angle
FROM experiments.rmp10_aalborg_intersection1 x1
JOIN experiments.rmp10_aalborg_intersection1 x2
ON x1.endpoint = x2.startpoint
AND not x1.internal
AND not x2.internal;

CREATE OR REPLACE VIEW experiments.rmp10_intersection1_left_swings AS
SELECT DISTINCT
	ARRAY[x1.segmentkey, x2.segmentkey, x3.segmentkey, x4.segmentkey] as segments,
	ARRAY[x1.startpoint, x2.startpoint, x3.startpoint, x4.startpoint, x4.endpoint] as points,
	ARRAY[x1.segmentgeo, x2.segmentgeo, x3.segmentgeo, x4.segmentgeo] as geoms,
	ST_Union(ARRAY[x1.segmentgeo, x2.segmentgeo, x3.segmentgeo, x4.segmentgeo]) as supersegmentgeom,
	experiments.circ(degrees(
		ST_Azimuth(ST_Startpoint(x2.segmentgeo), ST_Endpoint(x2.segmentgeo))
		- 
		ST_Azimuth(ST_Startpoint(x3.segmentgeo), ST_Endpoint(x3.segmentgeo)) 
	))
	as angle
FROM experiments.rmp10_aalborg_intersection1 x1
JOIN experiments.rmp10_aalborg_intersection1 x2
ON x1.endpoint = x2.startpoint 
AND not x1.internal 
AND x2.internal
JOIN experiments.rmp10_aalborg_intersection1 x3
ON x2.endpoint = x3.startpoint 
AND x3.internal
JOIN experiments.rmp10_aalborg_intersection1 x4
ON x3.endpoint = x4.startpoint 
AND not x4.internal;

CREATE OR REPLACE VIEW experiments.rmp10_intersection1_straight AS
SELECT DISTINCT
	ARRAY[x1.segmentkey, x2.segmentkey, x3.segmentkey] as segments,
	ARRAY[x1.startpoint, x2.startpoint, x3.startpoint, x3.endpoint] as points,
	ARRAY[x1.segmentgeo, x2.segmentgeo, x3.segmentgeo] as geoms,
	ST_Union(ARRAY[x1.segmentgeo, x2.segmentgeo, x3.segmentgeo]) as supersegmentgeom,
	experiments.circ(degrees(
		ST_Azimuth(ST_Startpoint(x1.segmentgeo), ST_Endpoint(x1.segmentgeo))
		- 
		ST_Azimuth(ST_Startpoint(x3.segmentgeo), ST_Endpoint(x3.segmentgeo)) 
	))
	as angle
FROM experiments.rmp10_aalborg_intersection1 x1
JOIN experiments.rmp10_aalborg_intersection1 x2
ON x1.endpoint = x2.startpoint 
AND not x1.internal 
AND x2.internal
JOIN experiments.rmp10_aalborg_intersection1 x3
ON x2.endpoint = x3.startpoint 
AND not x3.internal;

DROP TABLE IF EXISTS experiments.rmp10_intersection1_supersegments CASCADE;

CREATE TABLE experiments.rmp10_intersection1_supersegments AS
SELECT *, 'RIGHT' as direction FROM experiments.rmp10_intersection1_right_swings
UNION
SELECT *, 'LEFT' as direction FROM experiments.rmp10_intersection1_left_swings
UNION
SELECT *, 'STRAIGHT' as direction FROM experiments.rmp10_intersection1_straight;

CREATE OR REPLACE VIEW experiments.rmp10_intersection1_right_swings_trips AS
SELECT 
	x1.trip_id, 
	x1.id as id1, 
	x1.segmentkey as segmentkey1, 
	x1.trip_segmentno as trip_segmentno1, 
	x1.ev_kwh as ev_kwh1,
	x2.id as id2, 
	x2.segmentkey as segmentkey2, 
	x2.trip_segmentno as trip_segmentno2, 
	x2.ev_kwh as ev_kwh2
FROM (
	SELECT 
		segments[1] as in_seg,
		segments[2] as out_seg
	FROM experiments.rmp10_intersection1_supersegments
	WHERE direction = 'RIGHT'
) as rs
JOIN mapmatched_data.viterbi_match_osm_dk_20140101 x1
ON rs.in_seg = x1.segmentkey
JOIN mapmatched_data.viterbi_match_osm_dk_20140101 x2
ON rs.out_seg = x2.segmentkey
AND x1.trip_id = x2.trip_id
AND x1.trip_segmentno = x2.trip_segmentno - 1;

CREATE OR REPLACE VIEW experiments.rmp10_intersection1_averages AS
SELECT 
	segmentkey1, 
	segmentkey2, 
	avg_kwh_right, 
	avg(vit1.ev_kwh) + avg(vit2.ev_kwh) as avg_kwh_all
FROM (
	SELECT 
		segmentkey1, 
		segmentkey2, 
		avg(ev_kwh1) + avg(ev_kwh2) as avg_kwh_right
	FROM experiments.rmp10_intersection1_right_swings_trips
	GROUP BY segmentkey1, segmentkey2
) as trips
JOIN mapmatched_data.viterbi_match_osm_dk_20140101 vit1
ON vit1.segmentkey = segmentkey1
JOIN mapmatched_data.viterbi_match_osm_dk_20140101 vit2
ON vit2.segmentkey = segmentkey2
GROUP BY segmentkey1, segmentkey2, avg_kwh_right;

SELECT
	*,
	abs(avg_kwh_right - avg_kwh_all) as mean_abs_error,
	abs(avg_kwh_right - avg_kwh_all) / avg_kwh_all as mean_percentage_error
FROM experiments.rmp10_intersection1_averages;

