select 
	tripsegs.id, 
	tripsegs.trip_id,
	tripsegs.trip_segmentno,
	tripsegs.segmentkey,
	tripsegs.meters_segment,
	tripsegs.direction,
	tripsegs.ev_kwh as actual_ev_kwh,
	tripsegs.ev_kwh_trip,
	accum.actual_ev_kwh_trip,
	baseline.ev_wh / 1000 as baseline_ev_kwh,
	accum.baseline_ev_kwh_trip,
	CASE WHEN tripsegs.ev_kwh IS NOT NULL
		THEN abs((tripsegs.ev_kwh + 10) - (baseline.ev_wh / 1000 + 10)) -- +10 when calculating abs diff to avoid negative cases 
		ELSE NULL
    END AS baseline_abs_error,
	CASE WHEN tripsegs.ev_kwh IS NOT NULL
		THEN abs((tripsegs.ev_kwh + 10) - (baseline.ev_wh / 1000 + 10)) / meters_segment 
		ELSE NULL
    END AS baseline_abs_error_per_meter,
	segmodel.avg_wh / 1000 as model_ev_kwh,
	accum.model_ev_kwh_trip,
	CASE WHEN tripsegs.ev_kwh IS NOT NULL
		THEN abs((tripsegs.ev_kwh + 10) - (segmodel.avg_wh / 1000 + 10)) -- +10 when calculating abs diff to avoid negative cases 
		ELSE NULL
    END AS model_abs_error,
	CASE WHEN tripsegs.ev_kwh IS NOT NULL
		THEN abs((tripsegs.ev_kwh + 10) - (segmodel.avg_wh / 1000 + 10)) / meters_segment
		ELSE NULL
    END AS model_abs_error_per_meter,
	mapsegs.segmentgeo
from 
	mapmatched_data.viterbi_match_osm_dk_20140101 tripsegs, 
	maps.osm_dk_20140101 mapsegs,
	experiments.rmp10_baseline_segment_predictions baseline,
	experiments.rmp10_energy_errors segmodel,
		(select 
			tripsegs.trip_id,
			sum(tripsegs.ev_kwh) as actual_ev_kwh_trip,
			sum(baseline.ev_wh / 1000) as baseline_ev_kwh_trip,
			sum(segmodel.avg_wh / 1000) as model_ev_kwh_trip
		from 
			mapmatched_data.viterbi_match_osm_dk_20140101 tripsegs, 
			experiments.rmp10_baseline_segment_predictions baseline,
			experiments.rmp10_energy_errors segmodel
		where 
			tripsegs.trip_id=any(array[116699, 91881, 4537, 76966, 52557, 175355, 103715]) and
			tripsegs.segmentkey=baseline.segmentkey and
			tripsegs.segmentkey=segmodel.segmentkey
		group by tripsegs.trip_id) accum
where 
	tripsegs.trip_id=any(array[116699, 91881, 4537, 76966, 52557, 175355, 103715]) and
	tripsegs.segmentkey=mapsegs.segmentkey and
	tripsegs.segmentkey=baseline.segmentkey and
	tripsegs.segmentkey=segmodel.segmentkey and
	tripsegs.trip_id=accum.trip_id
order by tripsegs.trip_id, trip_segmentno

