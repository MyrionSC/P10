select 
	tripsegs.segmentkey, 
	mapseg.segmentgeo, 
	tripsegs.meters_segment, 
	tripsegs.ev_kwh * 1000 as real_ev_wh, 
	preds.ev_wh as pred_ev_wh, 
	abs(preds.ev_wh - (tripsegs.ev_kwh * 1000)) as abs_error, 
	abs(preds.ev_wh - (tripsegs.ev_kwh * 1000)) / tripsegs.meters_segment as abs_error_per_meter
from mapmatched_data.viterbi_match_osm_dk_20140101 tripsegs
join experiments.rmp10_energy_predictions preds
on tripsegs.id = preds.mapmatched_id
join maps.osm_dk_20140101 mapseg
on tripsegs.segmentkey = mapseg.segmentkey
order by meters_segment

