select t.id, t.point, t.geom, t.degree, t.segments
into experiments.rmp10_traffic_lights_single_3_degree
from 
	(
		select lightnodes.point
		from experiments.rmp10_trafic_light_nodes_within_10m lightnodes
		join experiments.rmp10_interesting_nodes inodes
		on lightnodes.point=inodes.point and lightnodes.degree=3
		EXCEPT
		select point
		from experiments.rmp10_intersections
	) p
join experiments.rmp10_trafic_light_nodes_within_10m t
on p.point=t.point


