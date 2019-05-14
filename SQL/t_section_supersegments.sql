select
	s1.point,
	s1.segmentkey as in_segkey,
	s1.segtype as in_segtype,
	s2.segmentkey as out_segkey,
	s2.segtype as out_segtype,
	array[s1.segmentkey, s2.segmentkey] as supersegment, 
	s1.segmentgeo as in_geo,
	s2.segmentgeo as out_geo,
	st_union(s1.segmentgeo::geometry, s2.segmentgeo::geometry) as geo
into experiments.rmp10_t_section_supersegments
from experiments.rmp10_t_section_segment_types s1
join experiments.rmp10_t_section_segment_types s2
on
	s1.point=s2.point and
	(s1.segtype='In' or s1.segtype='Both')  and 
	(s2.segtype='Out' or s2.segtype='Both') and
	s1.segmentkey!=s2.segmentkey
order by point, in_segkey, out_segkey

