select segkey as segmentkey, wsname 
into experiments.rmp10_segment_weatherstation_map
from (
	select tbl1.segkey, tbl1.mindist, tbl2.wsname
	from(	select segkey, min(distance) as mindist from (
			select seg.segmentkey as segkey, st_distance(seg.segmentgeo, ws.geog) as distance, ws.name as wsname
			from maps.osm_dk_20140101 seg, experiments.rmp10_yr_weatherstations ws) tbl3
			group by segkey
	) tbl1
	inner join (
		select seg.segmentkey as segkey, st_distance(seg.segmentgeo, ws.geog) as distance, ws.name as wsname
		from maps.osm_dk_20140101 seg, experiments.rmp10_yr_weatherstations ws) tbl2
	on tbl1.segkey=tbl2.segkey
	where tbl1.mindist=tbl2.distance
) tbl4
