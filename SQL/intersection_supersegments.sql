select
	s1.cid,
	s1.segmentkey as in_segkey,
	s1.segtype as in_segtype,
	s2.segmentkey as out_segkey,
	s2.segtype as out_segtype,
	array[s1.segmentkey] ||
		  experiments.rmp10_intersection_supersegment_internal_path(s1.segmentkey, s2.segmentkey, s1.cid) ||
		  array[s2.segmentkey] as supersegment
into experiments.rmp10_intersection_supersegments_v2
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

-- update supersegments with nice geostuff
update experiments.rmp10_intersection_supersegments as iss
SET 
	start_geo=sq.start_geo,
	end_geo=sq.end_geo,
	supersegment_geo=sq.supersegment_geo
FROM (
		SELECT 
			iiss.cid, 
			iiss.in_segkey, 
			iiss.out_segkey,
			st_union(startseg.segmentgeo::geometry) as start_geo, 
			st_union(endseg.segmentgeo::geometry) as end_geo,
			st_union(mss.segmentgeo::geometry) as supersegment_geo
		FROM experiments.rmp10_intersection_supersegments iiss
		JOIN maps.osm_dk_20140101 startseg
		ON iiss.in_segkey=startseg.segmentkey
		JOIN maps.osm_dk_20140101 endseg
		ON iiss.out_segkey=endseg.segmentkey
		JOIN (
			select cid, in_segkey, out_segkey, unnest(supersegment) as supersegs
			FROM experiments.rmp10_intersection_supersegments
		) supersegs
		on iiss.cid=supersegs.cid and iiss.in_segkey=supersegs.in_segkey and iiss.out_segkey=supersegs.out_segkey
		JOIN maps.osm_dk_20140101 mss
		on supersegs.supersegs=mss.segmentkey
		group by iiss.cid, iiss.in_segkey, iiss.out_segkey 
	) as sq
WHERE
	iss.cid=sq.cid and iss.in_segkey=sq.in_segkey and iss.out_segkey=sq.out_segkey;

