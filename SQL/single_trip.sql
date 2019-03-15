select segs.*, maps.segmentgeo as geo
from mapmatched_data.viterbi_match_osm_dk_20140101 segs, maps.osm_dk_20140101 maps
where segs.segmentkey=maps.segmentkey and trip_id=1220
order by trip_segmentno
