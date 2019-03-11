DROP VIEW IF EXISTS experiments.segments_temp_view;
CREATE VIEW experiments.segments_temp_view AS
SELECT
    trips_table.trip_id as trip_id,
    trips_table.trip_segmentno as trip_segmentno,
    trips_table.id as mapmatched_id,
    trips_table.segmentkey as segmentkey,
    osm_map.categoryid,
    CASE WHEN incline_table.incline_percentage IS NOT NULL
         THEN CASE WHEN trips_table.direction = 'BACKWARD'
                   THEN -incline_table.incline_percentage
                   ELSE incline_table.incline_percentage
              END 
         ELSE 0
    END AS incline,
    trips_table.meters_segment as segment_length,
    trips_table.speed / 3.6 as speed,
    weather_table.air_temperature as temperature,
    CASE WHEN wind_table.tailwind_magnitude IS NOT NULL
         THEN -wind_table.tailwind_magnitude 
         ELSE 0
    END as headwind_speed,
    time_table.quarter,
    time_table.hour,
    (time_table.hour / 2)::smallint as two_hour,
    (time_table.hour / 4)::smallint as four_hour,
    (time_table.hour / 6)::smallint as six_hour,
    (time_table.hour / 12)::smallint as twelve_hour,
    date_table.weekday,
    date_table.month,
    trips_table.ev_kwh,
    speedlimit_table.speedlimit,
    CASE WHEN inter_table.intersection THEN 1 ELSE 0 END as intersection
FROM experiments.mi904e18_training as trips_table, 
    maps.osm_dk_20140101 as osm_map,
    dims.dimdate as date_table, 
    dims.dimtime as time_table, 
    experiments.mi904e18_segment_incline as incline_table,
    dims.dimweathermeasure as weather_table, 
    experiments.mi904e18_wind_vectors as wind_table,
    experiments.mi904e18_speedlimits as speedlimit_table,
    experiments.rmp10_intersections as inter_table
WHERE trips_table.segmentkey = osm_map.segmentkey 
    AND trips_table.datekey = date_table.datekey 
    AND trips_table.timekey = time_table.timekey 
    AND trips_table.segmentkey = incline_table.segmentkey
    AND trips_table.weathermeasurekey = weather_table.weathermeasurekey
    AND trips_table.id = wind_table.vector_id
    AND trips_table.segmentkey = inter_table.segmentkey
    AND trips_table.ev_kwh IS NOT NULL
    AND trips_table.segmentkey = speedlimit_table.segmentkey;

\copy (SELECT * FROM experiments.segments_temp_view) TO '../Models/data/Data.csv' HEADER CSV;  

-- optional
DROP VIEW experiments.segments_temp_view;
