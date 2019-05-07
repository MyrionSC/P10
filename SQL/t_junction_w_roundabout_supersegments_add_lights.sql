ALTER TABLE experiments.rmp10_intersection_supersegments_t_junction_w_roundabout
ADD COLUMN lights integer[],
ADD COLUMN traffic_lights boolean;

update experiments.rmp10_intersection_supersegments_t_junction_w_roundabout as neww
set lights=sq.lights, traffic_lights=sq.traffic_lights
from (
	select segments, lights, traffic_lights
	from experiments.rmp10_intersection_supersegments_t_junction
) sq
where
	neww.segments=sq.segments;

-- where traffic_lights are null now are roundabout t-junctions. set these to false.
update experiments.rmp10_intersection_supersegments_t_junction_w_roundabout
set traffic_lights=false
where traffic_lights is null;


