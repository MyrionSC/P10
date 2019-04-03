with supersegs as (
select
	s1.cid,
	s1.segmentkey as in_segkey,
	s1.segtype as in_segtype,
	s2.segmentkey as out_segkey,
	s2.segtype as out_segtype,
	st_union(s1.segmentgeo::geometry, s2.segmentgeo::geometry) as geo
from experiments.rmp10_intersection_segment_types s1
join experiments.rmp10_intersection_segment_types s2
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
	



