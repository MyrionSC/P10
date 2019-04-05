select
	s1.cid_w_single,
	s1.segmentkey as in_segkey,
	s1.segtype as in_segtype,
	s2.segmentkey as out_segkey,
	s2.segtype as out_segtype,
	array[s1.segmentkey] ||
		  experiments.rmp10_intersection_supersegment_internal_path(s1.segmentkey, s2.segmentkey, s1.cid_w_single) ||
		  array[s2.segmentkey] as supersegment, 
	s1.segmentgeo as in_geo,
	s2.segmentgeo as out_geo
into experiments.rmp10_intersection_supersegments_v2
from experiments.rmp10_intersection_segment_types s1
join experiments.rmp10_intersection_segment_types s2
on 
	s1.cid_w_single=s2.cid_w_single and
	s1.segtype!='Internal' and
	s2.segtype!='Internal' and
	(s1.segtype='In' or s1.segtype='Both')  and 
	(s2.segtype='Out' or s2.segtype='Both') and
	s1.segmentkey!=s2.segmentkey
order by cid_w_single, in_segkey, out_segkey

-- update supersegments with nice geostuff
