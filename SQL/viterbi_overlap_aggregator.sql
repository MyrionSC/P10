UPDATE experiments.rmp10_viterbi_match_osm_dk_20140101_overlap os
SET ev_soc_trip = ev_soc_agg,
	meters_driven_trip = meters_driven_agg,
	meters_segment_trip = meters_segment_agg,
	seconds_trip = seconds_agg,
	ev_kwh_trip = ev_kwh_agg
FROM (
	SELECT 
		sum(ev_soc) OVER (
			PARTITION BY trip_id 
			ORDER BY trip_id, trip_segmentno
		) as ev_soc_agg,
		sum(meters_driven) OVER (
			PARTITION BY trip_id 
			ORDER BY trip_id, trip_segmentno
		) as meters_driven_agg,
		sum(meters_segment) OVER (
			PARTITION BY trip_id 
			ORDER BY trip_id, trip_segmentno
		) as meters_segment_agg,
		sum(seconds) OVER (
			PARTITION BY trip_id 
			ORDER BY trip_id, trip_segmentno
		) as seconds_agg,
		sum(ev_kwh) OVER (
			PARTITION BY trip_id 
			ORDER BY trip_id, trip_segmentno
		) as ev_kwh_agg,
		id
	FROM experiments.rmp10_viterbi_match_osm_dk_20140101_overlap
) ss
WHERE os.id = ss.id;