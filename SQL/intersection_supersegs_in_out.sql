--drop view inter_segs;
create OR REPLACE temp view inter_segs as (
select distinct(unnest(segments)) as segmentkey
from experiments.rmp10_intersections_aalborg
);

--drop view inter_points cascade;
create OR REPLACE temp view inter_points as (
select cid, array_agg(distinct(point)) as points
from experiments.rmp10_intersections_aalborg
group by cid
);

drop view intersection_segment_types cascade;
create OR REPLACE temp view intersection_segment_types as (
select 
	m.*,
	p.cid,
	CASE 
		When m.startpoint=any(p.points) and not m.endpoint=any(p.points) Then 'Out'
		When not m.startpoint=any(p.points) and m.endpoint=any(p.points) Then 'In'
		ELSE 'Internal'
	END as segtype
from inter_segs i
join maps.osm_dk_20140101 m
on i.segmentkey=m.segmentkey
join inter_points p
on m.startpoint=any(p.points) or m.endpoint=any(p.points)
);


--drop view out_segs;
create OR REPLACE temp view out_segs as (
	select segs as out_segs
	from (
		select segtype, array_agg(segmentkey) as segs
		from intersection_segment_types
		group by segtype
	) t1
	where segtype='Out'
);

select
	s1.cid,
	s1.segmentkey as in_segkey,
	s2.segmentkey as out_segkey,
	st_union(s1.segmentgeo::geometry, s2.segmentgeo::geometry) as geo
from intersection_segment_types s1
join intersection_segment_types s2
on s1.cid=s2.cid and s1.segtype='In' and s2.segtype='Out'


