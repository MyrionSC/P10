CREATE TABLE experiments.rmp10_wind AS
SELECT
	id,
	wind_direction,
	CASE WHEN wind_direction > 180
		 THEN 360 - wind_direction
		 ELSE wind_direction
	END AS symmetric_wind_direction,
	wind_speed_ms
FROM (
	SELECT 
		id, 
		experiments.circ(wind_direction - driving_direction) as wind_direction, 
		wind_speed_ms
	FROM (
		SELECT 
			vit.id, 
			we.wind_direction, 
			we.wind_speed_ms,
			CASE WHEN vit.direction = 'FORWARD'
				 THEN rd.road_direction
				 ELSE experiments.circ(rd.road_direction + 180)
			END as driving_direction
		FROM mapmatched_data.viterbi_match_osm_dk_20140101 vit
		JOIN (
			SELECT segmentkey, ST_Azimuth(ST_Startpoint(osm.segmentgeo::geometry), ST_Endpoint(osm.segmentgeo::geometry))::int as road_direction
			FROM maps.osm_dk_20140101 osm
		) as rd
		ON rd.segmentkey = vit.segmentkey
		JOIN dims.dimweathermeasure we
		ON we.weathermeasurekey = vit.weathermeasurekey
	) as temp1
) as temp2

CREATE INDEX experiments_rmp10_wind_id_idx
	ON experiments.rmp10_wind USING btree
	(id)
	TABLESPACE pg_default;