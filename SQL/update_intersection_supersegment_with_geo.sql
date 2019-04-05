ALTER TABLE experiments.rmp10_intersection_supersegments_v2
ADD COLUMN start_geo geometry,
ADD COLUMN end_geo geometry,
ADD COLUMN supersegment_geo geometry;

update experiments.rmp10_intersection_supersegments_v2 as iss
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
		FROM experiments.rmp10_intersection_supersegments_v2 iiss
		JOIN maps.osm_dk_20140101 startseg
		ON iiss.in_segkey=startseg.segmentkey
		JOIN maps.osm_dk_20140101 endseg
		ON iiss.out_segkey=endseg.segmentkey
		JOIN (
			select cid, in_segkey, out_segkey, unnest(supersegment) as supersegs
			FROM experiments.rmp10_intersection_supersegments_v2
		) supersegs
		on iiss.cid=supersegs.cid and iiss.in_segkey=supersegs.in_segkey and iiss.out_segkey=supersegs.out_segkey
		JOIN maps.osm_dk_20140101 mss
		on supersegs.supersegs=mss.segmentkey
		group by iiss.cid, iiss.in_segkey, iiss.out_segkey 
	) as sq
WHERE
	iss.cid=sq.cid and iss.in_segkey=sq.in_segkey and iss.out_segkey=sq.out_segkey;

