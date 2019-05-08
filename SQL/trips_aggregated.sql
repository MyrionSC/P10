DROP TABLE IF EXISTS experiments.rmp10_trips_aggregated;

select 
	trip_id,
	max(trip_segmentno) as trip_segments_count,
	array_agg(segmentkey) as segmentkeys_arr,
	array_agg(meters_driven) as meters_driven_arr,
	array_agg(seconds) as seconds_arr,
	array_agg(ev_kwh) as ev_kwh_arr,
	array_agg(datekey) as datekey_arr,
	array_agg(timekey) as timekey_arr
into experiments.rmp10_trips_aggregated
from (
	select *
	from mapmatched_data.viterbi_match_osm_dk_20140101
	order by trip_segmentno
) sq
group by trip_id;

CREATE INDEX rmp10_trips_aggregated_trip_idx
    ON experiments.rmp10_trips_aggregated USING btree
    (trip_id ASC NULLS LAST)
    TABLESPACE pg_default;
