select *
into experiments.rmp10_trafic_light_nodes_within_10m
from experiments.rmp10_traffic_lights tl
join experiments.rmp10_interesting_nodes n
on st_dwithin(
	ST_TRANSFORM(tl.way::geometry, 3857), 
	ST_TRANSFORM(n.geom::geometry, 3857),
	10)
