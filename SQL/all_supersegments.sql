Drop table if exists experiments.rmp10_all_supersegments;

select *
into experiments.rmp10_all_supersegments
from (
	select 
		segments,
		rmp10_internal_points(segments) as points,
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
		rmp10_internal_points(segments) as points,
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
		rmp10_internal_points(segments) as points,
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
		rmp10_internal_points(segments) as points,
		num_traversals,
		direction,
		null as categories,
		lights,
		traffic_lights,
		'Complex' as type
	from experiments.rmp10_intersection_supersegments_complex
) sq;

-- add height difference from other group
ALTER TABLE experiments.rmp10_all_supersegments
ADD COLUMN height_difference double precision;

UPDATE experiments.rmp10_all_supersegments as sups
SET height_difference=sssq.hd
FROM (
	select segments, type, sum(height_difference) as hd
	from (
		select sq.*, inc.height_difference
		from (
			select unnest(segments) as segment, segments, type
			from experiments.rmp10_all_supersegments
		) sq
		join experiments.bcj_incline inc
		on sq.segment = inc.segmentkey
	) ssq
	group by segments, type
) sssq
WHERE sups.segments=sssq.segments and sups.type=sssq.type

-- add categories to everything
UPDATE experiments.rmp10_all_supersegments AS sups
SET categories=ssq.categories
FROM (
	SELECT sq.segments, sq.type, array_agg(m.category) as categories
	FROM (
		SELECT unnest(segments) as segmentkey, segments, type
		FROM experiments.rmp10_all_supersegments
		WHERE categories is null
	) sq
	JOIN maps.osm_dk_20140101 m
	ON sq.segmentkey=m.segmentkey
	GROUP BY sq.segments, sq.type
) ssq
WHERE ssq.segments=sups.segments AND ssq.type=sups.type


-- indexes
CREATE INDEX rmp10_all_supersegments_segments_idx
    ON experiments.rmp10_all_supersegments USING btree
    (segments)
    TABLESPACE pg_default;
	
CREATE INDEX rmp10_all_supersegments_startpoint_idx
    ON experiments.rmp10_all_supersegments USING btree
    (startpoint)
    TABLESPACE pg_default;
	
CREATE INDEX rmp10_all_supersegments_endpoint_idx
    ON experiments.rmp10_all_supersegments USING btree
    (endpoint)
    TABLESPACE pg_default;
	
CREATE INDEX rmp10_all_supersegments_startseg_idx
    ON experiments.rmp10_all_supersegments USING btree
    (startseg)
    TABLESPACE pg_default;
	
CREATE INDEX rmp10_all_supersegments_endseg_idx
    ON experiments.rmp10_all_supersegments USING btree
    (endseg)
    TABLESPACE pg_default;
