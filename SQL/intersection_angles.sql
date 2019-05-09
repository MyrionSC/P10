WITH clusters AS (
	SELECT cid_w_single as cid, array_agg(point) as points
	FROM experiments.rmp10_intersections
	GROUP BY cid_w_single
), supersegs AS (
	SELECT 
		segs.*,
		CASE WHEN osm1.startpoint = ANY(clusters.points)
			 THEN 'OUT'
			 WHEN osm1.endpoint = ANY(clusters.points)
			 THEN 'IN'
		END AS indir,
		CASE WHEN osm2.startpoint = ANY(clusters.points)
			 THEN 'OUT'
			 WHEN osm2.endpoint = ANY(clusters.points)
			 THEN 'IN'
		END AS outdir,
		subgeoms(in_geo::geometry) as ingeoms,
		subgeoms(out_geo::geometry) as outgeoms
	FROM experiments.rmp10_intersection_supersegments_v2 segs
	JOIN clusters
	ON segs.cid_w_single = clusters.cid
	JOIN maps.osm_dk_20140101 osm1
	ON osm1.segmentkey = segs.in_segkey
	JOIN maps.osm_dk_20140101 osm2
	ON osm2.segmentkey = segs.out_segkey
	WHERE clusters.cid = 9581
), geoms AS (
SELECT
	cid_w_single, 
	in_segkey, 
	out_segkey,
	CASE WHEN indir = 'IN'
		 THEN ingeoms[array_length(ingeoms, 1)]
		 ELSE ST_Reverse(ingeoms[1])
	END AS in_geom,
	CASE WHEN outdir = 'OUT'
		 THEN outgeoms[1]
		 ELSE ST_Reverse(outgeoms[
			 array_length(outgeoms, 1)
		 ])
	END AS out_geom
FROM supersegs
), superseg_angles as (
	SELECT cid_w_single, in_segkey, out_segkey, in_geom, out_geom, experiments.circ(in_angle - out_angle) as angle
	FROM (
		SELECT 
			*, 
			degrees(ST_Azimuth(
				ST_Startpoint(in_geom), 
				ST_Endpoint(in_geom)
			)) as in_angle, 
			degrees(ST_Azimuth(
				ST_Startpoint(out_geom),
				ST_Endpoint(out_geom)
			)) as out_angle
		FROM geoms
	) sub
)
SELECT 
	*,
	CASE WHEN angle < 30 OR angle >= 330 THEN 'STRAIGHT'
		 WHEN angle >= 30 AND angle < 150 THEN 'LEFT'
		 WHEN angle >= 150 AND angle < 210 THEN 'U-TURN'
		 WHEN angle >= 210 AND angle < 330 THEN 'RIGHT'
	END as direction
FROM superseg_angles

CREATE FUNCTION dir_classifier(
	angle double precision,
	straight_tolerance integer,
	u_turn_tolerance integer
)
RETURNS text
LANGUAGE 'sql'
AS $$
SELECT 
	CASE WHEN angle >= 360 - st OR  angle < st 		 THEN 'STRAIGHT'
		 WHEN angle >= st 		AND angle < 180 - ut THEN 'LEFT'
		 WHEN angle >= 180 - ut AND angle < 180 + ut THEN 'U-TURN'
		 WHEN angle >= 180 + ut AND angle < 360 - st THEN 'RIGHT'
	END as direction
FROM (
	SELECT
		straight_tolerance / 2 as st,
		u_turn_tolerance / 2 as ut
) ts
$$