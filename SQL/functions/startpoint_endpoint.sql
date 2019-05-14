CREATE OR REPLACE FUNCTION rmp10_endpoint(segments integer[])
RETURNS integer
LANGUAGE 'sql'

AS $$
SELECT CASE WHEN NOT (seg_points[2] = ANY(nxt_points) OR seg_points[1] = ANY(nxt_points))
			THEN NULL
	        WHEN seg_points[1] = ANY(nxt_points) 
			THEN seg_points[2] 
			ELSE seg_points[1] 
		END
FROM (
	SELECT 
		segmentkey,
		ARRAY[rmp10_startpoint(segmentkey), rmp10_endpoint(segmentkey)] as seg_points,
		ARRAY[rmp10_startpoint(nxt), rmp10_endpoint(nxt)] as nxt_points
	FROM (
		SELECT segmentkey, LEAD(segmentkey) OVER (ORDER BY array_position(segments, segmentkey) DESC) as nxt
		FROM (
			SELECT unnest(segments) as segmentkey, segments
		) sub
		LIMIT 1
	) sub1
) sub2
$$M

CREATE OR REPLACE FUNCTION rmp10_startpoint(segments integer[])
RETURNS integer
LANGUAGE 'sql'

AS $$
SELECT CASE WHEN NOT (seg_points[2] = ANY(nxt_points) OR seg_points[1] = ANY(nxt_points))
			THEN NULL
	        WHEN seg_points[1] = ANY(nxt_points) 
			THEN seg_points[1] 
			ELSE seg_points[2] 
		END
FROM (
	SELECT 
		segmentkey,
		ARRAY[rmp10_startpoint(segmentkey), rmp10_endpoint(segmentkey)] as seg_points,
		ARRAY[rmp10_startpoint(nxt), rmp10_endpoint(nxt)] as nxt_points
	FROM (
		SELECT segmentkey, LEAD(segmentkey) OVER (ORDER BY array_position(segments, segmentkey) DESC) as nxt
		FROM (
			SELECT unnest(segments) as segmentkey, segments
		) sub
		LIMIT 1
	) sub1
) sub2
$$;