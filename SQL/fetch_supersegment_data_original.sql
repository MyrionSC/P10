DROP VIEW IF EXISTS experiments.supersegments_temp_view_original;
CREATE VIEW experiments.supersegments_temp_view_original AS
	SELECT
		ats.trip_id,
		sups.segments, -- maybe not this
		sups.type, -- maybe not this
		sups.direction,
		sups.traffic_lights,
		sups.height_difference,
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
	FROM experiments.rmp10_all_supersegments_original sups
	JOIN experiments.rmp10_all_trip_supersegments_original ats -- only take those that overlaps with rmp10_training
	ON sups.superseg_id=ats.superseg_id
	UNION
	SELECT
		t.trip_id,
		array[t.segmentkey] as segments,
		'Segment'::text as type,
		'Straight'::text as direction,
		False as traffic_lights,
		inc.height_difference,
		s.category as cat_start,
		s.category as cat_end,
		0 as cat_speed_difference,
		t.meters_driven,
		t.meters_segment,
		t.weathermeasurekey,
		t.seconds,
		CASE 
			WHEN e.ev_kwh_from_ev_watt IS null THEN t.ev_kwh
			ELSE e.ev_kwh_from_ev_watt
		END AS ev_wh,
		t.datekey,
		t.timekey
	FROM experiments.rmp10_training t
	JOIN maps.osm_dk_20140101 s 
	ON t.segmentkey=s.segmentkey
	LEFT OUTER JOIN experiments.bcj_ev_watt_data e
	ON t.id=e.id
	JOIN experiments.bcj_incline inc
	ON t.segmentkey=inc.segmentkey;


\copy (SELECT * FROM experiments.supersegments_temp_view_original limit 100) TO '../Models/data/supersegment-data-original.csv' HEADER CSV;  
