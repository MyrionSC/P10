select s.ev_kwh as actual, p.ev_kwh as estimate, abs((s.ev_kwh+1) - (p.ev_kwh+1)) as abs_error, s.*, m.*
from experiments.rmp10_predictions_defaultenergy_epochs_20 p
join mapmatched_data.viterbi_match_osm_dk_20140101 s
on p.mapmatched_id=s.id
join maps.osm_dk_20140101 m
on s.segmentkey=m.segmentkey
where s.trip_id=227670
