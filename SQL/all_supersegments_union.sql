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
) sq
