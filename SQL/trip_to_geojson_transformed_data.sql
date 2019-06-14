WITH trip AS (
	SELECT *
	FROM experiments.rmp10_all_trip_data
	WHERE trip_id = 202094
	ORDER BY start_segmentno
), trip_vals AS (
	SELECT 
		trip.superseg_id,
		trip.start_segmentno,
		trip.ev_wh as actual, 
		sum(trip.ev_wh) OVER (ORDER BY trip.start_segmentno) as agg_actual,
		pred.ev_wh as pred, 
		sum(pred.ev_wh) OVER (ORDER BY trip.start_segmentno) as agg_pred,
		osm.startpoint, 
		osm.endpoint, 
		osm.meters,
		rmp10_get_geo(segments) as segmentgeo
	FROM trip
	JOIN experiments.rmp10_predictions_finalsupersegmodel_iter1 pred
	ON pred.id = trip.atd_id
	JOIN experiments.rmp10_all_osm_data osm
	ON osm.superseg_id = trip.superseg_id
	OR osm.segmentkey = trip.segmentkey
)
SELECT row_to_json(fc)::text as path
FROM (
	SELECT
		'FeaturesCollection' as "type",
		array_to_json(array_agg(f)) as "features"
	FROM (
		SELECT
			'Feature' as "type",
			ST_AsGeoJson(segmentgeo::geometry, 6)::json as "geometry",
			json_build_object(
				'actual', actual,
				'predicted', pred,
				'trip_actual', agg_actual,
				'trip_predicted', agg_pred,
				'startpoint', startpoint,
				'endpoint', endpoint,
				'id', superseg_id,
				'segmentno', start_segmentno,
				'length', meters
			)::json as "properties"
		FROM trip_vals
	) as f
) as fc;

WITH trip AS (
	SELECT *, vit.id as vitid
	FROM mapmatched_data.viterbi_match_osm_dk_20140101 vit
	JOIN experiments.bcj_ev_watt_data wd
	ON wd.id = vit.id
	WHERE trip_id = 202094
	ORDER BY trip_segmentno
), trip_vals AS (
	SELECT 
		trip.vitid as id,
		trip.trip_segmentno,
		trip.ev_kwh_from_ev_watt * 1000 as actual, 
		sum(trip.ev_kwh_from_ev_watt * 1000) OVER (ORDER BY trip.trip_segmentno) as agg_actual,
 		pred.ev_kwh * 1000 as pred, 
		sum(pred.ev_kwh * 1000) OVER (ORDER BY trip.trip_segmentno) as agg_pred,
		osm.startpoint, 
		osm.endpoint, 
		osm.meters,
		osm.segmentgeo as segmentgeo
	FROM trip
	JOIN experiments.rmp10_predictions_defaultenergy_epochs_20 pred
	ON pred.mapmatched_id = trip.vitid
	JOIN maps.osm_dk_20140101 osm
	ON osm.segmentkey = trip.segmentkey
)
SELECT row_to_json(fc)::text as path
FROM (
	SELECT
		'FeaturesCollection' as "type",
		array_to_json(array_agg(f)) as "features"
	FROM (
		SELECT
			'Feature' as "type",
			ST_AsGeoJson(segmentgeo::geometry, 6)::json as "geometry",
			json_build_object(
				'actual', actual,
				'predicted', pred,
				'trip_actual', agg_actual,
				'trip_predicted', agg_pred,
				'startpoint', startpoint,
				'endpoint', endpoint,
				'id', id,
				'segmentno', trip_segmentno,
				'length', meters
			)::json as "properties"
		FROM trip_vals
	) as f
) as fc;

WITH trip AS (
	SELECT *, vit.id as vitid
	FROM mapmatched_data.viterbi_match_osm_dk_20140101 vit
	JOIN experiments.bcj_ev_watt_data wd
	ON wd.id = vit.id
	WHERE trip_id = 202094
	ORDER BY trip_segmentno
), trip_vals AS (
	SELECT 
		trip.vitid as id,
		trip.trip_segmentno,
		trip.ev_kwh_from_ev_watt * 1000 as actual, 
		sum(trip.ev_kwh_from_ev_watt * 1000) OVER (ORDER BY trip.trip_segmentno) as agg_actual,
 		pred.ev_kwh * 1000 as pred, 
		sum(pred.ev_kwh * 1000) OVER (ORDER BY trip.trip_segmentno) as agg_pred,
		osm.startpoint, 
		osm.endpoint, 
		osm.meters,
		osm.segmentgeo as segmentgeo
	FROM trip
	JOIN experiments.rmp10_predictions_bestmodel pred
	ON pred.mapmatched_id = trip.vitid
	JOIN maps.osm_dk_20140101 osm
	ON osm.segmentkey = trip.segmentkey
)
SELECT row_to_json(fc)::text as path
FROM (
	SELECT
		'FeaturesCollection' as "type",
		array_to_json(array_agg(f)) as "features"
	FROM (
		SELECT
			'Feature' as "type",
			ST_AsGeoJson(segmentgeo::geometry, 6)::json as "geometry",
			json_build_object(
				'actual', actual,
				'predicted', pred,
				'trip_actual', agg_actual,
				'trip_predicted', agg_pred,
				'startpoint', startpoint,
				'endpoint', endpoint,
				'id', id,
				'segmentno', trip_segmentno,
				'length', meters
			)::json as "properties"
		FROM trip_vals
	) as f
) as fc;