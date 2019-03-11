select tripseg.trip_id, tripseg.trip_segmentno, tripseg.segmentkey, mapseg.segmentgeo
into experiments.rmp10_aalborg_start_trips
from 
	mapmatched_data.viterbi_match_osm_dk_20140101 tripseg,
	maps.osm_dk_20140101 mapseg,
	(select segs.trip_id				
	      from experiments.rmp10_aalborg_routing aalsegs, mapmatched_data.viterbi_match_osm_dk_20140101 segs
          where aalsegs.segmentkey=segs.segmentkey and segs.trip_segmentno=1) org_aal
where tripseg.trip_id=org_aal.trip_id and tripseg.segmentkey=mapseg.segmentkey

