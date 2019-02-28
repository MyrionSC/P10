SELECT
	osm.segmentkey,
	segmentgeo,
	avg(abs(pred.ev_wh - (ev_kwh * 1000)) / meters_segment) as error_per_meter
FROM experiments.rmp10_energy_predictions pred
JOIN mapmatched_data.viterbi_match_osm_dk_20140101 mm
ON pred.mapmatched_id = mm.id
JOIN maps.osm_dk_20140101 osm
ON osm.segmentkey = mm.segmentkey
GROUP BY osm.segmentkey, segmentgeo;