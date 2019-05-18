DROP TABLE IF EXISTS experiments.rmp10_training_supersegments_original;
SELECT
	sups.superseg_id,
	ats.trip_id,
	ats.id_arr::integer[],
	sups.type,
	sups.direction,
	sups.traffic_lights,
	sups.height_difference, -- change to incline
	sups.categories[1] as cat_start,
	sups.categories[array_length(sups.categories, 1)] as cat_end,
	sups.cat_speed_difference,
	ats.meters_driven,
	ats.meters_segment,
	ats.weathermeasurekey,
	ats.seconds,
	ats.ev_wh,
	ats.datekey,
	ats.timekey
INTO experiments.rmp10_training_supersegments_original
FROM experiments.rmp10_all_supersegments_original sups
JOIN experiments.rmp10_all_trip_supersegments_original ats
ON 
	sups.superseg_id=ats.superseg_id AND
	EXISTS (
		SELECT 
		FROM experiments.rmp10_training
		WHERE id=any(ats.id_arr)
	);

-- insert single segments from trainingset not encompassed by supersegments
INSERT INTO experiments.rmp10_training_supersegments_original (superseg_id, trip_id, id_arr, type, direction, 
	traffic_lights, height_difference, cat_start, cat_end, cat_speed_difference, meters_driven, 
	meters_segment, weathermeasurekey, seconds, ev_wh, datekey, timekey)
SELECT
	-1 as superseg_id,
	t.trip_id,
	array[t.id] as id_arr,
	'Segment'::text as type,
	'STRAIGHT'::text as direction,
	False as traffic_lights,
	inc.height_difference, -- change to incline
	s.category as cat_start,
	s.category as cat_end,
	0 as cat_speed_difference,
	t.meters_driven,
	t.meters_segment,
	t.weathermeasurekey,
	t.seconds,
	e.ev_kwh_from_ev_watt AS ev_wh,
	t.datekey,
	t.timekey
FROM experiments.rmp10_training t
JOIN maps.osm_dk_20140101 s 
ON t.segmentkey=s.segmentkey
JOIN experiments.bcj_ev_watt_data e -- we don't want nulls anyway
ON t.id=e.id
JOIN experiments.bcj_incline inc
ON t.segmentkey=inc.segmentkey
WHERE NOT EXISTS (
	SELECT 
	FROM (
		select unnest(id_arr) as unnested_id
		from experiments.rmp10_training_supersegments_original
	) sq
	WHERE t.id=sq.unnested_id
);

-- No indexes necessary, as we download everything every time

