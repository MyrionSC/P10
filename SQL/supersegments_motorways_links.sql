drop table if exists experiments.rmp10_supersegments_motorway_links;
create table experiments.rmp10_supersegments_motorway_links as
(select 
	array[links.segmentkey, motors.segmentkey] as supersegment, 
	st_union(links.segmentgeo::geometry, motors.segmentgeo::geometry) as geo,
	'exit'::text as direction
from experiments.rmp10_aalborg_segments links
join experiments.rmp10_aalborg_segments motors
on
	links.category='motorway_link' and 
	motors.category='motorway' and
	links.startpoint=motors.endpoint);

insert into experiments.rmp10_supersegments_motorway_links (supersegment, geo, direction)
select 
	array[links.segmentkey, motors.segmentkey] as supersegment, 
	st_union(links.segmentgeo::geometry, motors.segmentgeo::geometry) as geo,
	'entry'::text as direction
from experiments.rmp10_aalborg_segments links
join experiments.rmp10_aalborg_segments motors
on
	links.category='motorway_link' and 
	motors.category='motorway' and
	links.endpoint=motors.startpoint


