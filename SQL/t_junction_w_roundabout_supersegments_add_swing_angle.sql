ALTER TABLE experiments.rmp10_t_junction_w_roundabout_supersegments
ADD COLUMN angle double precision,
ADD COLUMN direction text;

UPDATE experiments.rmp10_t_junction_w_roundabout_supersegments ss
SET angle=sq.angle, direction=sq.direction
FROM (
	WITH supersegs AS (
		SELECT 
			segs.*,	
			CASE WHEN osm1.startpoint = segs.point
				 THEN 'OUT'
				 WHEN osm1.endpoint = segs.point
				 THEN 'IN'
			END AS indir,
			CASE WHEN osm2.startpoint = segs.point
				 THEN 'OUT'
				 WHEN osm2.endpoint = segs.point
				 THEN 'IN'
			END AS outdir,
			subgeoms(rmp10_get_geo(array[segments[1]])) as ingeoms,
			subgeoms(rmp10_get_geo(array[segments[2]])) as outgeoms
		FROM experiments.rmp10_t_junction_w_roundabout_supersegments segs
		JOIN maps.osm_dk_20140101 osm1
		ON osm1.segmentkey = segs.in_segkey
		JOIN maps.osm_dk_20140101 osm2
		ON osm2.segmentkey = segs.out_segkey
	), geoms AS (
		SELECT
			point, 
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
		SELECT point, in_segkey, out_segkey, in_geom, out_geom, experiments.circ(in_angle - out_angle) as angle
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
) sq
WHERE ss.point=sq.point and ss.in_segkey=sq.in_segkey and ss.out_segkey=sq.out_segkey
