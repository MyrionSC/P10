DROP VIEW experiments.rmp10_category_shift_supersegments;
CREATE TABLE experiments.rmp10_category_shift_supersegments (
	superseg_id BIGSERIAL,
	segments integer[]
);

INSERT INTO experiments.rmp10_category_shift_supersegments (segments)
WITH category_shifts AS (
	SELECT *
	FROM experiments.rmp10_interesting_nodes
	WHERE degree = 2
)
SELECT 
	ARRAY[osm1.segmentkey, osm2.segmentkey] as segments
FROM category_shifts nods
JOIN maps.osm_dk_20140101 osm1
ON nods.point = ANY(ARRAY[osm1.startpoint, osm1.endpoint])
JOIN maps.osm_dk_20140101 osm2
ON nods.point = ANY(ARRAY[osm2.startpoint, osm2.endpoint])
AND osm1.segmentkey <> osm2.segmentkey
AND (osm1.endpoint=ANY(ARRAY[osm2.startpoint, osm2.endpoint])
OR osm1.startpoint=ANY(ARRAY[osm2.startpoint, osm2.endpoint]));

CREATE TABLE experiments.rmp10_roundabout_supersegments (
	superseg_id BIGSERIAL,
	roundabout_id bigint,
	segments integer[]
);

SELECT
	osm1.segmentkey as seg1,
	osm2.segmentkey as seg2,
	osm1.category as category1,
	osm2.category as category2,
	vit1.ev_kwh + vit2.ev_kwh as ev_kwh
FROM experiments.rmp10_category_shift_supersegments ss
JOIN maps.osm_dk_20140101 osm1
ON osm1.segmentkey = segments[1]
JOIN maps.osm_dk_20140101 osm2
ON osm2.segmentkey = segments[2]
JOIN mapmatched_data.viterbi_match_osm_dk_20140101 vit1
ON vit1.segmentkey = osm1.segmentkey
AND vit1.ev_kwh IS NOT NULL
JOIN mapmatched_data.viterbi_match_osm_dk_20140101 vit2
ON vit2.segmentkey = osm2.segmentkey
AND vit2.trip_id = vit1.trip_id
AND vit1.trip_segmentno = vit2.trip_segmentno - 1
AND vit2.ev_kwh IS NOT NULL

WITH externals as (
	WITH internal_points as (
		SELECT 
			array_agg(startpoint) FILTER (WHERE internal) as int_points,
			roundabout_id 
		FROM experiments.rmp10_roundabouts
		GROUP BY roundabout_id
	)
	SELECT 
		ext, 
		tmp.roundabout_id, 
		CASE WHEN direction = 'BOTH'
			 THEN CASE WHEN osm.endpoint=ANY(int_points)
				  THEN 'BOTH_IN'
			 	  ELSE 'BOTH_OUT'
			 END
			 ELSE CASE WHEN osm.endpoint=ANY(int_points)
				  THEN 'IN'
				  ELSE 'OUT' 
			 END
		END as direction
	FROM (
		SELECT unnest(external_segs) as ext, roundabout_id
		FROM experiments.rmp10_roundabout_superseg_temp
		WHERE roundabout_id = 1
	) as tmp
	JOIN maps.osm_dk_20140101 osm
	ON tmp.ext = osm.segmentkey
	JOIN internal_points ints
	ON ints.roundabout_id = tmp.roundabout_id
)
SELECT
	ext1.ext as entry,
	ext2.ext as exit,
	ext1.direction as in_dir,
	ext2.direction as out_dir,
	ext1.roundabout_id
FROM externals ext1
JOIN externals ext2
ON ext1.roundabout_id = ext2.roundabout_id
AND ext1.direction=ANY(ARRAY['BOTH_IN', 'BOTH_OUT', 'IN'])
AND ext2.direction=ANY(ARRAY['BOTH_IN', 'BOTH_OUT', 'OUT'])

CREATE FUNCTION experiments.rmp10_roundabout_supersegs (entry_seg integer, exit_seg integer, round_id bigint)
	   RETURNS integer[]
	   LANGUAGE 'sql'
AS $$
WITH RECURSIVE pathing(current_point, exit_point, entry, exit, path, i) AS (
	WITH base AS (
		SELECT 
			tmp.entry,
			tmp.exit,
			CASE WHEN in_dir=ANY(ARRAY['IN', 'BOTH_IN'])
				 THEN osm1.endpoint
				 ELSE osm1.startpoint
			END AS entry_point,
			CASE WHEN out_dir=ANY(ARRAY['OUT', 'BOTH_OUT'])
				 THEN osm2.startpoint
				 ELSE osm2.endpoint
			END AS exit_point
		FROM experiments.rmp10_roundabouts_entry_exit tmp
		JOIN maps.osm_dk_20140101 osm1
		ON osm1.segmentkey = entry
		AND entry = entry_seg
		AND roundabout_id = round_id
		JOIN maps.osm_dk_20140101 osm2
		ON osm2.segmentkey = exit
		AND exit = exit_seg
		AND roundabout_id = round_id
	)
	SELECT 
		entry_point as current_point,
		exit_point,
		entry,
		exit,
		ARRAY[entry] as path,
		0 as i
	FROM base
	UNION ALL
	SELECT
		nxt.endpoint as current_point,
		prv.exit_point,
		prv.entry,
		prv.exit,
		prv.path || nxt.segmentkey,
		prv.i+1
	FROM experiments.rmp10_roundabouts nxt
	JOIN pathing prv
	ON prv.current_point = nxt.startpoint
	AND prv.current_point != nxt.endpoint
	AND (prv.current_point <> prv.exit_point OR prv.i = 0)
	AND nxt.internal
	AND nxt.roundabout_id = round_id
)
SELECT path || exit as path
FROM pathing
ORDER BY row_number() OVER () DESC
LIMIT 1;
$$;

UPDATE experiments.rmp10_roundabouts
SET roundabout_id = new_id
FROM (
	SELECT osm_id as line_id, row_number() OVER (ORDER BY osm_id) as new_id
	FROM (
		SELECT distinct osm_id
		FROM experiments.rmp10_roundabouts
	) sub1
) sub2
WHERE osm_id = line_id

CREATE TABLE experiments.rmp10_uninteresting_nodes AS
SELECT * 
FROM (
	SELECT * 
	FROM experiments.rmp10_all_points
	WHERE degree <= 2
) sub1
WHERE NOT EXISTS (
	SELECT
	FROM experiments.rmp10_interesting_nodes
	WHERE point = sub1.point
)