with inter_segs as (
select distinct(unnest(segments)) as segmentkey
from experiments.rmp10_intersections_v2
), inter_points as (
	select cid_w_single, array_agg(distinct(point)) as points
	from experiments.rmp10_intersections_v2
	group by cid_w_single
)
select 
	m.*,
	p.cid_w_single,
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

