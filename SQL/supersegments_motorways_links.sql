drop table if exists experiments.rmp10_supersegments_motorway_links;
create table experiments.rmp10_supersegments_motorway_links as
(select 
 	links.segmentkey as link_segment,
	array[links.segmentkey, motors.segmentkey] as supersegment, 
	st_union(links.segmentgeo::geometry, motors.segmentgeo::geometry) as geo,
	'exit'::text as direction
from maps.osm_dk_20140101 links
join maps.osm_dk_20140101 motors
on
	links.category='motorway_link' and 
	motors.category='motorway' and
	links.startpoint=motors.endpoint);

insert into experiments.rmp10_supersegments_motorway_links (link_segment, supersegment, geo, direction)
select 
 	links.segmentkey as link_segment,
	array[links.segmentkey, motors.segmentkey] as supersegment, 
	st_union(links.segmentgeo::geometry, motors.segmentgeo::geometry) as geo,
	'entry'::text as direction
from maps.osm_dk_20140101 links
join maps.osm_dk_20140101 motors
on
	links.category='motorway_link' and 
	motors.category='motorway' and
	links.endpoint=motors.startpoint




