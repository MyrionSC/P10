select *
into experiments.rmp10_t_sections
from experiments.rmp10_interesting_nodes n
where 
	not EXISTS (
		select 
		from experiments.rmp10_intersections_v2 i
		where n.point=i.point
	) and
	not EXISTS(
		select
		from experiments.rmp10_roundabouts r
		where r.internal and (n.point=r.endpoint or n.point=r.startpoint)
	)

