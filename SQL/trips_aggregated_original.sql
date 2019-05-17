DROP TABLE IF EXISTS experiments.rmp10_trips_aggregated_original;

select 
	trip_id,
	max(trip_segmentno) as trip_segments_count,
	array_agg(segmentkey) as segmentkeys_arr,
	array_agg(meters_segment) as meters_segment_arr,
	array_agg(meters_driven) as meters_driven_arr,
	array_agg(speed) as speed_arr,
	array_agg(height_difference) as height_difference_arr,
	array_agg(incline) as incline_arr,
	array_agg(weathermeasurekey) as weathermeasurekey_arr,
	array_agg(seconds) as seconds_arr,
	array_agg(updated_ev_kwh) as ev_kwh_arr,
	array_agg(datekey) as datekey_arr,
	array_agg(timekey) as timekey_arr,
	array_agg(id) as id_arr
into experiments.rmp10_trips_aggregated_original
from (
	select 
		v.*,
		CASE 
			WHEN e.ev_kwh_from_ev_watt IS null THEN v.ev_kwh
			ELSE e.ev_kwh_from_ev_watt
		END AS updated_ev_kwh,
		CASE
			WHEN v.direction='FORWARD' THEN i.height_difference
			ELSE i.height_difference * -1
		END AS height_difference,
		CASE
			WHEN v.direction='FORWARD' THEN i.incline
			ELSE i.incline * -1
		END AS incline
	from mapmatched_data.viterbi_match_osm_dk_20140101 v
	left outer join experiments.bcj_ev_watt_data e
	on v.id=e.id
	join experiments.bcj_incline i
	on v.segmentkey=i.segmentkey
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


