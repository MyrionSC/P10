/*drop table experiments.rmp10_complex_segmenttypes;

CREATE TABLE experiments.rmp10_complex_segmenttypes AS
WITH inter_segs as (
	SELECT unnest(segments) as segmentkey, cid
	FROM experiments.rmp10_intersections_v2
	WHERE cid IS NOT NULL
), inter_points AS (
	SELECT cid, array_agg(distinct(point)) as points
	FROM experiments.rmp10_intersections_v2
	WHERE cid IS NOT NULL
	GROUP BY cid
)
SELECT
	m.segmentkey,
	p.cid,
	CASE
		when m.startpoint = any(p.points) and m.endpoint = any(p.points) Then 'Internal'
		when m.direction ='BOTH' Then 'Both'
		When m.startpoint = any(p.points) and not m.endpoint = any(p.points) Then 'Out'
		When not m.startpoint = any(p.points) and m.endpoint = any(p.points) Then 'In'
	END as segtype
from inter_segs i
join maps.osm_dk_20140101 m
on i.segmentkey = m.segmentkey
join inter_points p
on m.startpoint = any(p.points) or m.endpoint = any(p.points);*/

drop table experiments.rmp10_complex_intersection_supersegments;

select distinct
	s1.cid,
	s1.segmentkey
	|| experiments.rmp10_complex_intersection_internal_path(s1.segmentkey, s2.segmentkey, s1.cid)
	|| s2.segmentkey as segments
into experiments.rmp10_complex_intersection_supersegments
from experiments.rmp10_complex_segmenttypes s1
join experiments.rmp10_complex_segmenttypes s2
on s1.cid=s2.cid 
--and s1.segtype!='Internal' and s2.segtype!='Internal' 
and	(s1.segtype = 'In' or s1.segtype = 'Both') 
and (s2.segtype = 'Out' or s2.segtype = 'Both') 
and	s1.segmentkey <> s2.segmentkey
order by cid, segments;