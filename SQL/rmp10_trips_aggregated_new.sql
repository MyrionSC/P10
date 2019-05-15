DROP TABLE IF EXISTS experiments.rmp10_trips_aggregated_new;

select 
	trip_id,
	max(trip_segmentno) as trip_segments_count,
	array_agg(segmentkey) as segmentkeys_arr,
	array_agg(meters_segment) as meters_segment_arr,
	array_agg(meters_driven) as meters_driven_arr,
	array_agg(speed) as speed_arr,
	array_agg(weathermeasurekey) as weathermeasurekey_arr,
	array_agg(seconds) as seconds_arr,
	array_agg(ev_kwh) as ev_kwh_arr,
	array_agg(datekey) as datekey_arr,
	array_agg(timekey) as timekey_arr
into experiments.rmp10_trips_aggregated_new
from (
	SELECT * 
	FROM experiments.rmp10_viterbi_match_osm_dk_20140101_overlap_new 
	ORDER BY trip_id, trip_segmentno
) sub
group by trip_id;

CREATE INDEX rmp10_trips_aggregated_trip_original_idx_new
    ON experiments.rmp10_trips_aggregated_new USING btree
    (trip_id ASC NULLS LAST)
    TABLESPACE pg_default;
CREATE INDEX rmp10_trips_aggregated_trip_original_segmentkeys_arr_idx_new
    ON experiments.rmp10_trips_aggregated_new USING gin
    (segmentkeys_arr)
    TABLESPACE pg_default;

