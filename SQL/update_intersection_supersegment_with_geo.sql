ALTER TABLE experiments.rmp10_intersection_supersegments_v2
ADD COLUMN supersegment_geo geometry;

update experiments.rmp10_intersection_supersegments_v2 as iss
SET 
	supersegment_geo=sq.supersegment_geo
FROM (
		SELECT 
			iiss.cid_w_single, 
			iiss.in_segkey, 
			iiss.out_segkey,
			st_union(mss.segmentgeo::geometry) as supersegment_geo
		FROM experiments.rmp10_intersection_supersegments_v2 iiss
		JOIN (
			select cid_w_single, in_segkey, out_segkey, unnest(supersegment) as supersegs
			FROM experiments.rmp10_intersection_supersegments_v2
		) supersegs
		on iiss.cid_w_single=supersegs.cid_w_single and iiss.in_segkey=supersegs.in_segkey and iiss.out_segkey=supersegs.out_segkey
		JOIN maps.osm_dk_20140101 mss
		on supersegs.supersegs=mss.segmentkey
		group by iiss.cid_w_single, iiss.in_segkey, iiss.out_segkey 
	) as sq
WHERE
	iss.cid_w_single=sq.cid_w_single and iss.in_segkey=sq.in_segkey and iss.out_segkey=sq.out_segkey;


