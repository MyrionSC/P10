select s.trip_id, sum(s.ev_kwh) as actual, sum(p.ev_kwh) as estimate, 
	abs(sum(s.ev_kwh) - sum(p.ev_kwh)) as abs_error, sum(meters_driven) as meters_driven,
	abs(sum(s.ev_kwh) - sum(p.ev_kwh)) / sum(meters_driven) as abs_error_per_meter_driven
from experiments.rmp10_predictions_defaultenergy_epochs_20 p
join mapmatched_data.viterbi_match_osm_dk_20140101 s
on p.mapmatched_id=s.id
group by s.trip_id
order by abs_error_per_meter_driven desc
