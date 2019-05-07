Drop table if exists experiments.rmp10_intersection_supersegments;

select *
into experiments.rmp10_intersection_supersegments
from (
	select 
		segments,
		num_traversals,
		direction,
		lights,
		traffic_lights,
		'T' as type
	from experiments.rmp10_intersection_supersegments_t_junction_w_roundabout
	UNION
	select 
		segments,
		num_traversals,
		direction,
		lights,
		traffic_lights,
		'Simple' as type
	from experiments.rmp10_intersection_supersegments_simple
	UNION 
	select
		segments,
		num_traversals,
		direction,
		lights,
		traffic_lights,
		'Complex' as type
	from experiments.rmp10_intersection_supersegments_complex
) sq
