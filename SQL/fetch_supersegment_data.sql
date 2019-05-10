DROP VIEW IF EXISTS experiments.supersegments_temp_view;
CREATE VIEW experiments.supersegments_temp_view AS
-- supersegments
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
FROM experiments.rmp10_all_supersegments sups
JOIN experiments.rmp10_all_trip_supersegments ats
ON sups.segments=ats.segments AND sups.type=ats.type
UNION
-- segments
SELECT
	t.trip_id,
	array[t.segmentkey] as segments,
	'Segment' as type,
	null as direction,
	null as traffic_lights,
	inc.height_difference,
	s.category as cat_start,
	s.category as cat_end,
	0 as cat_speed_difference,
	t.meters_driven,
	t.meters_segment,
	t.weathermeasurekey,
	t.seconds,
	t.ev_kwh * 1000 as ev_wh,
	t.datekey,
	t.timekey
FROM experiments.rmp10_training t
JOIN maps.osm_dk_20140101 s 
ON t.segmentkey=s.segmentkey
JOIN experiments.bcj_incline inc
ON t.segmentkey=inc.segmentkey


\copy (SELECT * FROM experiments.supersegments_temp_view) TO '../Models/data/supersegment-data.csv' HEADER CSV;  

-- optional
DROP VIEW experiments.supersegments_temp_view;
