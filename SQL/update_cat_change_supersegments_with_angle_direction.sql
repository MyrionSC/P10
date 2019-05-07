ALTER TABLE experiments.rmp10_category_change_supersegs
ADD COLUMN angle double precision,
ADD COLUMN direction text;

UPDATE experiments.rmp10_category_change_supersegs as ccs
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
			subgeoms(osm1.segmentgeo::geometry) as ingeoms,
			subgeoms(osm2.segmentgeo::geometry) as outgeoms
		FROM experiments.rmp10_category_change_supersegs segs
		JOIN maps.osm_dk_20140101 osm1
		ON osm1.segmentkey = segs.segments[1]
		JOIN maps.osm_dk_20140101 osm2
		ON osm2.segmentkey = segs.segments[2]
	), geoms AS (
	SELECT
		point, 
		segments[1] as in_segkey, 
		segments[2] as out_segkey,
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
WHERE 
	ccs.point=sq.point AND
	ccs.segments[1]=sq.in_segkey AND
	ccs.segments[2]=sq.out_segkey


