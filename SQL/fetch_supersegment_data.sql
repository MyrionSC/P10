DROP VIEW IF EXISTS experiments.supersegments_training_data_temp_view;
CREATE VIEW experiments.supersegments_training_data_temp_view AS
WITH osm AS (
	SELECT 
		superseg_id,
		null as segmentkey,
		segments,
		categories[1] as cat_start,
		categories[array_length(categories, 1)] as cat_end,
		cat_speed_difference,
		traffic_lights,
		type
	FROM experiments.rmp10_all_supersegments
	UNION
	SELECT 
		null as superseg_id,
		segmentkey,
		array[segmentkey] as segments,
		category as cat_start,
		category as cat_end,
		0 as cat_speed_difference,
		false as traffic_lights,
		'Segment' as type
	FROM experiments.rmp10_osm_dk_20140101_overlaps
)
SELECT 
	atd.superseg_id,
	atd.segmentkey,
	atd.trip_id,
	osm.segments,
	osm.type,
	osm.cat_start,
	osm.cat_end,
	osm.cat_speed_difference,
	osm.traffic_lights,
	atd.meters_segment as segment_length,
	atd.meters_driven,
	atd.seconds,
	atd.incline,
	atd.ev_wh,
	-- dunno if speed makes sense
	-- wind vector is possible, then we just need a join to origin id
	time_table.quarter,
	weather_table.air_temperature as temperature,
	date_table.weekday,
	date_table.month
FROM experiments.rmp10_all_trip_data atd
JOIN osm osm
ON atd.superseg_id=osm.superseg_id OR atd.segmentkey=osm.segmentkey
JOIN dims.dimdate date_table
ON atd.datekey = date_table.datekey
JOIN dims.dimtime time_table
ON atd.timekey = time_table.timekey
JOIN dims.dimweathermeasure weather_table
ON atd.weathermeasurekey = weather_table.weathermeasurekey
WHERE EXISTS (
	SELECT
	FROM (
		SELECT v.id
		FROM experiments.rmp10_training t
		JOIN experiments.rmp10_viterbi_match_osm_dk_20140101_overlap v
		ON t.id=v.origin
	) sq
	WHERE sq.id=any(atd.id_arr)
);

\copy (SELECT * FROM experiments.supersegments_training_data_temp_view) TO '../Models/data/supersegment-data.csv' HEADER CSV;

