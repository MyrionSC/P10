DROP TABLE IF EXISTS experiments.rmp10_trips_aggregated_original;

select 
	trip_id,
	max(trip_segmentno) as trip_segments_count,
	array_agg(segmentkey) as segmentkeys_arr,
	array_agg(meters_segment) as meters_segment_arr,
	array_agg(meters_driven) as meters_driven_arr,
	array_agg(speed) as speed_arr,
	array_agg(weathermeasurekey) as weathermeasurekey_arr,
	array_agg(seconds) as seconds_arr,
	array_agg(updated_ev_kwh) as ev_kwh_arr,
	array_agg(datekey) as datekey_arr,
	array_agg(timekey) as timekey_arr
into experiments.rmp10_trips_aggregated_original
from (
	select v.*, e.ev_kwh as updated_ev_kwh
	from mapmatched_data.viterbi_match_osm_dk_20140101 v
	join experiments.ev_kwh_update e
	on v.trip_id=e.trip_id
	order by trip_id, trip_segmentno
) sq
group by trip_id;

CREATE INDEX rmp10_trips_aggregated_trip_original_idx
    ON experiments.rmp10_trips_aggregated_original USING btree
    (trip_id ASC NULLS LAST)
    TABLESPACE pg_default;
CREATE INDEX rmp10_trips_aggregated_trip_original_segmentkeys_arr_idx
    ON experiments.rmp10_trips_aggregated_original USING gin
    (segmentkeys_arr)
    TABLESPACE pg_default;

