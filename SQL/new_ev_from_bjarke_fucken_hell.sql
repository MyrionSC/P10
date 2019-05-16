UPDATE experiments.rmp10_viterbi_match_osm_dk_20140101_overlap os
SET ev_kwh = sub.ev_kwh_from_ev_watt
FROM experiments.bcj_ev_watt_data sub
WHERE sub.id = os.origin
AND os.id = os.origin;

UPDATE experiments.rmp10_viterbi_match_osm_dk_20140101_overlap os
SET ev_kwh = sub.ev_kwh_from_ev_watt / 2
FROM experiments.bcj_ev_watt_data sub
WHERE sub.id = os.origin
AND os.id != os.origin;