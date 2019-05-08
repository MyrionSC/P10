DROP TABLE IF EXISTS experiments.rmp10_all_trip_supersegments;

select
	s1.trip_id,
	s1.trip_segmentno as start_segmentno,
	s2.trip_segmentno as end_segmentno,
	sups.*
into experiments.rmp10_all_trip_supersegments
from experiments.rmp10_all_supersegments sups
join mapmatched_data.viterbi_match_osm_dk_20140101 s1
on sups.segments[1]=s1.segmentkey
join mapmatched_data.viterbi_match_osm_dk_20140101 s2
on 
	sups.segments[array_length(segments, 1)]=s2.segmentkey and
	s1.trip_id=s2.trip_id and
	s1.trip_segmentno=s2.trip_segmentno - array_length(segments, 1) + 1

