--drop view inter_segs;
create OR REPLACE temp view inter_segs as (
	select distinct(unnest(segments)) as segmentkey
	from experiments.rmp10_intersections
);

--drop view inter_points cascade;
create OR REPLACE temp view inter_points as (
	select cid, array_agg(distinct(point)) as points
	from experiments.rmp10_intersections
	group by cid
);

--drop view intersection_segment_types cascade;
create OR REPLACE temp view intersection_segment_types as (
select 
	m.*,
	p.cid,
	CASE 
		when m.startpoint=any(p.points) and m.endpoint=any(p.points) Then 'Internal'
		when m.direction='BOTH' Then 'Both'
		When m.startpoint=any(p.points) and not m.endpoint=any(p.points) Then 'Out'
		When not m.startpoint=any(p.points) and m.endpoint=any(p.points) Then 'In'
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

with supersegs as (
select
	s1.cid,
	s1.segmentkey as in_segkey,
	s1.segtype as in_segtype,
	s2.segmentkey as out_segkey,
	s2.segtype as out_segtype,
	st_union(s1.segmentgeo::geometry, s2.segmentgeo::geometry) as geo
from intersection_segment_types s1
join intersection_segment_types s2
on 
	s1.cid=s2.cid and
	s1.segtype!='Internal' and
	s2.segtype!='Internal' and
	(s1.segtype='In' or s1.segtype='Both')  and 
	(s2.segtype='Out' or s2.segtype='Both') and
	s1.segmentkey!=s2.segmentkey
order by cid, in_segkey, out_segkey
) 
select *
from supersegs s1
join supersegs s2
on 
	s1.cid!=s2.cid and
	(s1.in_segkey=s2.out_segkey or s1.out_segkey=s2.in_segkey)
	



