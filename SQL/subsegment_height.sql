/* The SQL statements in this file finds the subsegments of each segment in the osm maps data
 * and calculates the incline of each of those subsegments using the raster data.
 */

/* Creates a table to contain the subsegment data.
 * Has seven columns:
 *  subsegment_id, primary key
 *  segmentkey, the id of the segment, which the subsegment is from
 *  subsegment_num, the order of the subsegments in the segment
 *  subsegmentgeo, the geography of the subsegment
 *  height_change, the incline of the subsegment
 *  startpoint_height, the height value at that startpoint
 *  endpoint_height, the height value at that endpoint
 */
CREATE TABLE experiments.mi904e18_subsegment_incline (
	subsegment_id BIGSERIAL,
	segmentkey bigint,
	subsegment_num integer,
	subsegmentgeo geometry,
	height_change double precision,
	startpoint_height double precision,
	endpoint_height double precision,
	PRIMARY KEY(subsegment_id)
);


/* Gets the closest height value of each of the points calculated in the inner query
 * from the raster data and inserts it into the table.
 */
INSERT INTO experiments.mi904e18_subsegment_incline(segmentkey, subsegment_num, subsegmentgeo, height_change, startpoint_height, endpoint_height)
SELECT 
	startpoint_part.segmentkey,
	startpoint_part.subsegment_num,
	ST_MakeLine(startpoint_part.startpoint, endpoint_part.endpoint) as subsegmentgeo,
	endpoint_part.height - startpoint_part.height as height_change,
	startpoint_part.height as startpoint_height,
	endpoint_part.height as endpoint_height
FROM (
	/* Calculates the height value for the startpoints of each subsegment, 
	 * by selecting the nearest value from the raster 
	 */
	SELECT
		startpoint_calc.segmentkey,
		startpoint_calc.segmentgeo,
		startpoint_calc.startpoint,
		ST_NearestValue(raster.rast, 1, startpoint_calc.startpoint) as height,
		startpoint_calc.subsegment_num
	FROM experiments.mi904e18_heightmapbridge raster CROSS JOIN (
		/* Generates the startpoints of each subsegment in each segment
		 */
		SELECT
			segmentkey,
			segmentgeo,
			ST_PointN(
				segmentgeo::geometry, 
				generate_series(1, ST_NPoints(segmentgeo::geometry)-1)
			) as startpoint,
			generate_series(1, ST_NPoints(segmentgeo::geometry)-1) as subsegment_num
		FROM maps.osm_dk_20140101
		WHERE category != 'ferry'
	) as startpoint_calc
	WHERE ST_intersects(raster.rast, startpoint_calc.startpoint)
) as startpoint_part JOIN (
	/* Calculates the height value for the endpoints of each subsegment, 
	 * by selecting the nearest value from the raster 
	 */
	SELECT
		endpoint_calc.segmentkey,
		endpoint_calc.endpoint,
		ST_NearestValue(raster.rast, 1, endpoint_calc.endpoint) as height,
		endpoint_calc.subsegment_num
	FROM experiments.mi904e18_heightmapbridge raster CROSS JOIN (
		/* Generates the endpoints of each subsegment in each segment
		 */
		SELECT
			segmentkey,
			ST_PointN(
				segmentgeo::geometry,
				generate_series(2, ST_NPoints(segmentgeo::geometry))
			) as endpoint,
			generate_series(1, ST_NPoints(segmentgeo::geometry)-1) as subsegment_num
		FROM maps.osm_dk_20140101
		WHERE category != 'ferry'
	) as endpoint_calc
	WHERE ST_intersects(raster.rast, endpoint_calc.endpoint)
) as endpoint_part 
ON startpoint_part.segmentkey = endpoint_part.segmentkey
AND startpoint_part.subsegment_num = endpoint_part.subsegment_num

/* Create indexes to improve select speed
 */
CREATE INDEX experiments_subsegment_incline_subsegment_id_idx
    ON experiments.mi904e18_subsegment_incline USING btree
    (subsegment_id)
	TABLESPACE pg_default;
	
CREATE INDEX experiments_subsegment_incline_segmentkey_idx
    ON experiments.mi904e18_subsegment_incline USING btree
    (segmentkey)
	TABLESPACE pg_default;
	
CREATE INDEX experiments_subsegment_incline_subsegment_num_idx
    ON experiments.mi904e18_subsegment_incline USING btree
    (subsegment_num)
	TABLESPACE pg_default;

CREATE INDEX experiments_subsegment_incline_height_change_idx
    ON experiments.mi904e18_subsegment_incline USING btree
    (height_change)
	TABLESPACE pg_default;

CREATE INDEX experiments_subsegment_incline_startpoint_height_idx
    ON experiments.mi904e18_subsegment_incline USING btree
    (startpoint_height)
	TABLESPACE pg_default;
	
CREATE INDEX experiments_subsegment_incline_endpoint_height_idx
    ON experiments.mi904e18_subsegment_incline USING btree
    (endpoint_height)
	TABLESPACE pg_default;

/* Calculate the segment incline, as well as angle */
CREATE TABLE experiments.mi904e18_segment_incline(
	segmentkey bigint,
	startpoint_height double precision,
	endpoint_height double precision,
	incline double precision,
	incline_angle double precision,
	incline_percentage double precision,
	PRIMARY KEY(segmentkey)
);

INSERT INTO experiments.mi904e18_segment_incline(segmentkey, startpoint_height, endpoint_height, incline, incline_angle, incline_percentage)
SELECT 
	sp.segmentkey, 
	sp.height as startpoint_height, 
	ep.height as endpoint_height,
	ep.height - sp.height as incline,
	CASE WHEN sp.meters > 0 THEN degrees(ATAN((ep.height - sp.height) / sp.meters))
		ELSE 0 END as angle,
	CASE WHEN sp.meters > 0 THEN ((ep.height - sp.height) / sp.meters) * 100
		ELSE 0 END as percentage
FROM (
	SELECT 
		segmentkey, 
		AVG(ST_NearestValue(rast, 1, ST_Startpoint(segmentgeo::geometry))) as height,
		meters
	FROM maps.osm_dk_20140101
	JOIN experiments.mi904e18_heightmapbridge
	ON ST_Intersects(rast, ST_Startpoint(segmentgeo::geometry))
) as sp
JOIN (
	SELECT 
		segmentkey,
		AVG(ST_NearestValue(rast, 1, ST_Endpoint(segmentgeo::geometry))) as height
	FROM maps.osm_dk_20140101
	JOIN experiments.mi904e18_heightmapbridge
	ON ST_Intersects(rast, ST_Endpoint(segmentgeo::geometry))
    GROUP BY segmentkey
) as ep
ON sp.segmentkey = ep.segmentkey ON CONFLICT DO NOTHING

CREATE INDEX experiments_mi904e18_segment_incline_segmentkey_idx
	ON experiments.mi904e18_segment_incline USING btree
	(segmentkey)
	TABLESPACE pg_default;

CREATE INDEX experiments_mi904e18_segment_incline_incline_idx
	ON experiments.mi904e18_segment_incline USING btree
	(incline)
	TABLESPACE pg_default;

CREATE INDEX experiments_mi904e18_segment_incline_incline_angle_idx
	ON experiments.mi904e18_segment_incline USING btree
	(incline_angle)
	TABLESPACE pg_default;
	
CREATE INDEX experiments_mi904e18_segment_incline_incline_percentage_idx
	ON experiments.mi904e18_segment_incline USING btree
	(incline_percentage)
	TABLESPACE pg_default;