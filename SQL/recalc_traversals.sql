UPDATE experiments.rmp10_all_supersegments
SET num_traversals = 0;

UPDATE experiments.rmp10_all_supersegments att
SET num_traversals = sub.num_traversals
FROM (
	select superseg_id, count(*) as num_traversals
	from (
		select
			sups.superseg_id,
			s1.trip_id,
			s1.trip_segmentno as start_segmentno,
			s2.trip_segmentno as end_segmentno,
			sups.segments,
			sups.type
		--into experiments.rmp10_all_trip_supersegments
		from experiments.rmp10_all_supersegments sups
		join mapmatched_data.viterbi_match_osm_dk_20140101 s1
		on sups.segments[1]=s1.segmentkey
		join mapmatched_data.viterbi_match_osm_dk_20140101 s2
		on
			sups.segments[array_length(segments, 1)]=s2.segmentkey and
			s1.trip_id=s2.trip_id and
			s1.trip_segmentno=s2.trip_segmentno - array_length(segments, 1) + 1
	) sq
	join experiments.rmp10_trips_aggregated_original ta
	on
		sq.trip_id=ta.trip_id and
		sq.segments=ta.segmentkeys_arr[sq.start_segmentno:sq.end_segmentno]
	group by superseg_id
) sub
WHERE sub.superseg_id = att.superseg_id