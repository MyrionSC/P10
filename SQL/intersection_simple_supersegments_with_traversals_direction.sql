with inter_segs as (
	select unnest(segments) as segmentkey, point
	from experiments.rmp10_intersections_v2
	where cid is null
), segment_types as (
	select
		m.segmentkey,
		i.point,
		CASE 
			when m.direction='BOTH' Then 'Both'
			When m.startpoint=i.point and not m.endpoint=i.point Then 'Out'
			When not m.startpoint=i.point and m.endpoint=i.point Then 'In'
		END as segtype
	--into experiments.rmp10_intersection_simple_segment_types_v2
	from inter_segs i
	join maps.osm_dk_20140101 m
	on i.segmentkey=m.segmentkey
	
), supersegments as (
	select
		s1.point,
		array[s1.segmentkey] || array[s2.segmentkey] as segments
	--into experiments.rmp10_intersection_supersegments_v2
	from segment_types s1
	join segment_types s2
	on 
		s1.point=s2.point and
		(s1.segtype='In' or s1.segtype='Both') and 
		(s2.segtype='Out' or s2.segtype='Both') and
		s1.segmentkey <> s2.segmentkey
	order by point
), supersegments_w_traversals_temp as (
	select
		point,
		segments,
		count(*) as num_traversals
	from supersegments ss
	join mapmatched_data.viterbi_match_osm_dk_20140101 s1
	on ss.segments[1]=s1.segmentkey
	join mapmatched_data.viterbi_match_osm_dk_20140101 s2
	on 
		ss.segments[2]=s2.segmentkey and
		s1.trip_id=s2.trip_id and
		s1.trip_segmentno=s2.trip_segmentno - 1
	group by point, segments
), supersegments_w_traversals as (
	select ss.*, CASE WHEN sswt.num_traversals IS NOT NULL THEN sswt.num_traversals ELSE 0 END as num_traversals
	from supersegments ss
	left outer join supersegments_w_traversals_temp sswt
	ON ss.segments = sswt.segments
	AND ss.point = sswt.point
)
select ss.*, sq.direction
INTO experiments.rmp10_intersection_supersegments_simple
from supersegments_w_traversals ss
join (
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
		FROM supersegments_w_traversals segs
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
ON
	ss.point=sq.point AND
	ss.segments[1]=sq.in_segkey AND
	ss.segments[2]=sq.out_segkey

