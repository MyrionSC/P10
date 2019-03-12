select 
	tripsegs.id, 
	tripsegs.trip_id,
	tripsegs.trip_segmentno,
	tripsegs.segmentkey,
	tripsegs.direction,
	tripsegs.ev_kwh as actual_ev_kwh,
	baseline.ev_wh / 1000 as baseline_ev_kwh,
	CASE WHEN tripsegs.ev_kwh IS NOT NULL
		THEN abs((tripsegs.ev_kwh + 10) - (baseline.ev_wh / 1000 + 10)) -- +10 when calculating abs diff to avoid negative cases 
		ELSE NULL
    END AS baseline_abs_error,
	segmodel.avg_wh / 1000 as model_ev_kwh,
	CASE WHEN tripsegs.ev_kwh IS NOT NULL
		THEN abs((tripsegs.ev_kwh + 10) - (segmodel.avg_wh / 1000 + 10)) -- +10 when calculating abs diff to avoid negative cases 
		ELSE NULL
    END AS model_abs_error,
	mapsegs.segmentgeo
from 
	mapmatched_data.viterbi_match_osm_dk_20140101 tripsegs, 
	maps.osm_dk_20140101 mapsegs,
	experiments.rmp10_baseline_segment_predictions baseline,
	experiments.rmp10_energy_errors segmodel
where 
	tripsegs.trip_id=any(array[77064]) and
	tripsegs.segmentkey=mapsegs.segmentkey and
	tripsegs.segmentkey=baseline.segmentkey and
	tripsegs.segmentkey=segmodel.segmentkey
order by trip_id, trip_segmentno
