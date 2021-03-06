Drop table if exists experiments.rmp10_all_supersegments_original;

select *
into experiments.rmp10_all_supersegments_original
from (
	select 
		segments,
		segments[1] as startseg,
		segments[array_length(segments, 1)] as endseg,
		startpoint,
		endpoint,
		array[point] as points,
		num_traversals,
		direction,
		categories,
		null as lights,
		null as traffic_lights,
		'Cat' as type
	from experiments.rmp10_category_change_supersegs
	UNION
	select 
		segments,
		segments[1] as startseg,
		segments[array_length(segments, 1)] as endseg,
		startpoint,
		endpoint,
		array[point] as points,
		num_traversals,
		direction,
		null as categories,
		lights,
		traffic_lights,
		'T' as type
	from experiments.rmp10_intersection_supersegments_t_junction_w_roundabout
	UNION
	select 
		segments,
		segments[1] as startseg,
		segments[array_length(segments, 1)] as endseg,
		startpoint,
		endpoint,
		array[point] as points,
		num_traversals,
		direction,
		null as categories,
		lights,
		traffic_lights,
		'Simple' as type
	from experiments.rmp10_intersection_supersegments_simple
	UNION 
	select
		segments,
		segments[1] as startseg,
		segments[array_length(segments, 1)] as endseg,
		startpoint,
		endpoint,
		array_remove(array_remove(rmp10_get_points(segments), startpoint), endpoint) as points,
		num_traversals,
		direction,
		null as categories,
		lights,
		traffic_lights,
		'Complex' as type
	from experiments.rmp10_intersection_supersegments_complex
) sq;

CREATE INDEX rmp10_all_supersegments_original_segments_array_idx
ON experiments.rmp10_all_supersegments_original
USING GIN(segments);

-- remove cat changes that is subset of others. WARNING: This took 9 seconds last we ran it
DELETE
from experiments.rmp10_all_supersegments_original s1
where s1.type='Cat'
and exists (
	select 
	from experiments.rmp10_all_supersegments_original
	where s1.segments <@ segments AND type!='Cat'
);

-- add height difference from other group
ALTER TABLE experiments.rmp10_all_supersegments_original
ADD COLUMN height_difference double precision;

UPDATE experiments.rmp10_all_supersegments_original as sups
SET height_difference=sssq.hd
FROM (
	select segments, type, sum(height_difference) as hd
	from (
		select sq.*, inc.height_difference
		from (
			select unnest(segments) as segment, segments, type
			from experiments.rmp10_all_supersegments_original
		) sq
		join experiments.bcj_incline inc
		on sq.segment = inc.segmentkey
	) ssq
	group by segments, type
) sssq
WHERE sups.segments=sssq.segments and sups.type=sssq.type;

-- add categories to everything
UPDATE experiments.rmp10_all_supersegments_original AS sups
SET categories=ssq.categories
FROM (
	SELECT sq.segments, sq.type, array_agg(m.category) as categories
	FROM (
		SELECT unnest(segments) as segmentkey, segments, type
		FROM experiments.rmp10_all_supersegments_original
		WHERE categories is null
	) sq
	JOIN maps.osm_dk_20140101 m
	ON sq.segmentkey=m.segmentkey
	GROUP BY sq.segments, sq.type
) ssq
WHERE ssq.segments=sups.segments AND ssq.type=sups.type;

-- add cat speed difference
ALTER TABLE experiments.rmp10_all_supersegments_original
ADD COLUMN cat_speed_difference double precision;

UPDATE experiments.rmp10_all_supersegments_original as s
SET cat_speed_difference=sq.cat_speed_difference
FROM (
	select 
		segments, 
		type, 
		categories, 
		categories[1] as firstcat, 
		s1.speed_avg,
		categories[array_length(categories, 1)] as lastcat,
		s2.speed_avg,
		s2.speed_avg - s1.speed_avg as cat_speed_difference
	from experiments.rmp10_all_supersegments_original sups
	JOIN experiments.rmp10_category_avg_speed s1
	ON sups.categories[1]=s1.category
	JOIN experiments.rmp10_category_avg_speed s2
	ON sups.categories[array_length(categories, 1)]=s2.category
) sq
WHERE s.segments=sq.segments AND s.type=sq.type;

-- add lights to type Category
UPDATE experiments.rmp10_all_supersegments_original s
SET lights=array[l.point], traffic_lights=true
from experiments.rmp10_trafic_light_nodes_within_30m l
where l.point=s.points[1] and s.type='Cat';

-- indexes
CREATE INDEX rmp10_all_supersegments_original_segments_idx
    ON experiments.rmp10_all_supersegments_original USING btree
    (segments)
    TABLESPACE pg_default;
	
CREATE INDEX rmp10_all_supersegments_original_startpoint_idx
    ON experiments.rmp10_all_supersegments_original USING btree
    (startpoint)
    TABLESPACE pg_default;
	
CREATE INDEX rmp10_all_supersegments_original_endpoint_idx
    ON experiments.rmp10_all_supersegments_original USING btree
    (endpoint)
    TABLESPACE pg_default;
	
CREATE INDEX rmp10_all_supersegments_original_startseg_idx
    ON experiments.rmp10_all_supersegments_original USING btree
    (startseg)
    TABLESPACE pg_default;
	
CREATE INDEX rmp10_all_supersegments_original_endseg_idx
    ON experiments.rmp10_all_supersegments_original USING btree
    (endseg)
    TABLESPACE pg_default;

ALTER TABLE experiments.rmp10_all_supersegments_original
ADD COLUMN superseg_id BIGSERIAL;