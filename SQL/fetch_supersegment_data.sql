DROP VIEW IF EXISTS experiments.supersegments_training_data_temp_view;
CREATE VIEW experiments.supersegments_training_data_temp_view AS
SELECT 
	atd.atd_id as mapmatched_id,
	osm.aod_id as segmentkey,
	atd.superseg_id as superseg_id,
	atd.segmentkey as seg_id,
	atd.trip_id,
	osm.segments,
	osm.type,
	osm.categories[1] as cat_start,
	osm.categories[array_length(osm.categories, 1)] as cat_end,
	osm.cat_speed_difference,
	osm.direction,
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
FROM experiments.rmp10_supersegments_training_data atd
JOIN experiments.rmp10_all_osm_data osm
ON atd.superseg_id=osm.superseg_id OR atd.segmentkey=osm.segmentkey
JOIN dims.dimdate date_table
ON atd.datekey = date_table.datekey
JOIN dims.dimtime time_table
ON atd.timekey = time_table.timekey
JOIN dims.dimweathermeasure weather_table
ON atd.weathermeasurekey = weather_table.weathermeasurekey;

\copy (SELECT * FROM experiments.supersegments_training_data_temp_view) TO '../Models/data/supersegment-data.csv' HEADER CSV;
