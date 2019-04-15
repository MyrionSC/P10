CREATE OR REPLACE FUNCTION ev(segs integer[])
RETURNS TABLE (
	segmentkey integer, 
	avg_ev double precision
)
LANGUAGE 'sql'
AS $func$
SELECT 
	segmentkey, 
	avg(ev_kwh) 
FROM mapmatched_data.viterbi_match_osm_dk_20140101 vit 
JOIN (
	SELECT unnest(segs) as seg 
) segms
ON seg = segmentkey
GROUP BY segmentkey
$func$

DROP FUNCTION ev_given(integer[][]);

CREATE OR REPLACE FUNCTION ev_given(
	segs integer[][2]
)
RETURNS TABLE (
	seg integer,
	given integer,
	avg_ev double precision
)
LANGUAGE 'sql'
AS $$
SELECT seg, given, avg(vit1.ev_kwh)
FROM (
	SELECT pair[1] as seg, pair[2] as given
	FROM (
		SELECT reduce_dim(segs) as pair
	) sub
) sub2
JOIN mapmatched_data.viterbi_match_osm_dk_20140101 vit1
ON vit1.segmentkey = seg
JOIN mapmatched_data.viterbi_match_osm_dk_20140101 vit2
ON vit2.segmentkey = given
AND vit1.trip_id = vit2.trip_id
AND vit1.trip_segmentno = vit2.trip_segmentno + 1
GROUP BY seg, given
ORDER BY seg
$$;

DROP FUNCTION ev(text, text);

CREATE OR REPLACE FUNCTION get_vit_superseg(superseg_query text, target text)
RETURNS TABLE (
	segments integer[],
	ids bigint[],
	targets real[],
	trip_id integer
)
LANGUAGE 'plpgsql'
AS $$
BEGIN
RETURN QUERY EXECUTE 
'
WITH superseg AS (' || superseg_query || ')
SELECT segments, ids, targets, trip_id
FROM (
	SELECT
		array_agg(segmentkey) as segments_driven,
		sub.segments,
		array_agg(id) as ids,
		array_agg(target) as targets,
		trip_id
	FROM (
		SELECT 
			seg.*, 
			vit.id, 
			vit.trip_id, 
			vit.trip_segmentno, 
			vit.' || target || '::real as target,
			LAG(vit.trip_segmentno, 1) OVER (
				PARTITION BY seg.segments, vit.trip_id
				ORDER BY seg.segments, vit.trip_id, vit.trip_segmentno
			) as prv_segmentno
		FROM (
			SELECT unnest(segments) as segmentkey, segments
			FROM superseg
		) seg
		JOIN mapmatched_data.viterbi_match_osm_dk_20140101 vit
		ON seg.segmentkey = vit.segmentkey
		ORDER BY seg.segments, vit.trip_id, vit.trip_segmentno
	) sub
	WHERE (prv_segmentno = trip_segmentno - 1 OR prv_segmentno IS NULL)
	GROUP BY segments, trip_id
) sub2
WHERE segments_driven = segments
';
END
$$;

DROP FUNCTION ev_superseg(text);
CREATE OR REPLACE FUNCTION ev_superseg(
	superseg_query text)
    RETURNS TABLE(segments integer[], ev double precision) 
    LANGUAGE 'plpgsql'

    COST 100
    VOLATILE 
    ROWS 1000
AS $BODY$
BEGIN
RETURN QUERY EXECUTE 
'
WITH superseg AS (' || superseg_query || ')
SELECT segments, avg(ev_kwh)
FROM (
	SELECT
		array_agg(segmentkey) as segments_driven,
		sub.segments,
		sum(ev_kwh) as ev_kwh
	FROM (
		SELECT 
			seg.*, 
			vit.id, 
			vit.trip_id, 
			vit.trip_segmentno, 
			vit.ev_kwh as ev_kwh,
			LAG(vit.trip_segmentno, 1) OVER (
				PARTITION BY seg.segments, vit.trip_id
				ORDER BY seg.segments, vit.trip_id, vit.trip_segmentno
			) as prv_segmentno
		FROM (
			SELECT unnest(segments) as segmentkey, segments
			FROM superseg
		) seg
		JOIN mapmatched_data.viterbi_match_osm_dk_20140101 vit
		ON seg.segmentkey = vit.segmentkey
		ORDER BY seg.segments, vit.trip_id, vit.trip_segmentno
	) sub
	WHERE (prv_segmentno = trip_segmentno - 1 OR prv_segmentno IS NULL)
	GROUP BY segments, trip_id
) sub2
WHERE segments_driven = segments
GROUP BY segments
';
END
$BODY$;

CREATE OR REPLACE FUNCTION ev_indi_superseg(query text)
RETURNS TABLE (segments integer[], ev double precision)
LANGUAGE 'plpgsql'
AS $$
BEGIN
RETURN QUERY EXECUTE
'
WITH superseg AS (' || query || ')
SELECT segments, ev
FROM (
	SELECT segments, array_agg(segmentkey), sum(ev_kwh) as ev
	FROM (
		SELECT
			sub.segments,
			sub.segmentkey,
			avg(ev_kwh) as ev_kwh
		FROM (
			SELECT 
				seg.*, 
				vit.id, 
				vit.trip_id, 
				vit.trip_segmentno, 
				vit.ev_kwh as ev_kwh
			FROM (
				SELECT unnest(segments) as segmentkey, segments
				FROM superseg
			) seg
			JOIN mapmatched_data.viterbi_match_osm_dk_20140101 vit
			ON seg.segmentkey = vit.segmentkey
		) sub
		GROUP BY segments, segmentkey
		ORDER BY segments, array_position(segments, segmentkey)
	) sub2
	GROUP BY segments
) sub3
WHERE segments = array_agg
';
END $$;

DROP TABLE IF EXISTS experiments.rmp10_given_last_ev_supersegs;
CREATE TABLE experiments.rmp10_given_last_ev_supersegs AS
WITH superseg1 AS (
	SELECT superseg_id, segments
	FROM experiments.rmp10_driven_supersegments_2len
), single AS (
	SELECT superseg_id, segments, segmentkey, avg(ev_per_meter) as avg_ev_per_meter
	FROM (
		SELECT 
			superseg_id,
			sub.segments,
			sub.segmentkey,
			ev_per_meter,
			trip_id
		FROM (
			SELECT 
				seg.*, 
				vit.id, 
				vit.trip_id, 
				vit.trip_segmentno, 
				vit.ev_kwh / vit.meters_segment as ev_per_meter
			FROM (
				SELECT distinct superseg_id, segments[2] as segmentkey, segments
				FROM superseg1
			) seg
			JOIN mapmatched_data.viterbi_match_osm_dk_20140101 vit
			ON seg.segmentkey = vit.segmentkey
			AND vit.ev_kwh IS NOT NULL
		) sub
	) sub2
	GROUP BY superseg_id, segments, segmentkey
	ORDER BY superseg_id
), single_given_before AS (
	SELECT superseg_id, segments, segments_driven[2] as segmentkey, avg(evs[2]) as avg_ev_per_meter
	FROM (
		SELECT 
			superseg_id,
			array_agg(segmentkey) as segments_driven, 
			sub.segments, 
			array_agg(id) as ids, 
			array_agg(ev) as evs,
			trip_id
		FROM (
			SELECT seg.*, vit.id, vit.trip_id, vit.trip_segmentno, vit.ev_kwh / vit.meters_segment as ev,
				LAG(vit.trip_segmentno, 1) OVER (
					PARTITION BY seg.superseg_id, vit.trip_id 
					ORDER BY seg.superseg_id, vit.trip_id, vit.trip_segmentno
				) as prv_segmentno
			FROM (
				SELECT distinct superseg_id, unnest(segments) as segmentkey, segments
				FROM superseg1
			) seg
			JOIN mapmatched_data.viterbi_match_osm_dk_20140101 vit
			ON seg.segmentkey = vit.segmentkey
			AND vit.ev_kwh IS NOT NULL
			ORDER BY seg.superseg_id, vit.trip_id, vit.trip_segmentno
		) sub
		WHERE (prv_segmentno = trip_segmentno - 1 OR prv_segmentno IS NULL)
		GROUP BY superseg_id, trip_id, segments
	) sub2
	WHERE segments_driven = segments
	GROUP BY superseg_id, segments, segments_driven[2]
	ORDER BY superseg_id
)
SELECT t1.superseg_id, t1.segments, t1.avg_ev_per_meter as single_ev, t2.avg_ev_per_meter as given_ev
FROM single t1
JOIN single_given_before t2
ON t1.superseg_id = t2.superseg_id;

--CREATE TABLE experiments.rmp10_speedchange_given_last AS 
SELECT t1.*, osm.segmentgeo FROM (
	SELECT segments
	FROM experiments.rmp10_category_shift_supersegments
	UNION
	SELECT supersegment as segments
	FROM experiments.rmp10_supersegments_motorway_links
) t1
JOIN maps.osm_dk_20140101 osm 
ON osm.segmentkey = t1.segments[1]
WHERE NOT EXISTS (
	WITH calc AS(
		WITH superseg1 AS (
			SELECT segments
			FROM experiments.rmp10_category_shift_supersegments
			UNION
			SELECT supersegment as segments
			FROM experiments.rmp10_supersegments_motorway_links
		), single AS (
			SELECT segments, segmentkey, avg(ev_per_meter) as avg_ev_per_meter
			FROM (
				SELECT 
					sub.segments,
					sub.segmentkey,
					ev_per_meter,
					trip_id
				FROM (
					SELECT 
						seg.*, 
						vit.id, 
						vit.trip_id, 
						vit.trip_segmentno, 
						vit.ev_kwh / vit.meters_segment as ev_per_meter
					FROM (
						SELECT distinct segments[2] as segmentkey, segments
						FROM superseg1
					) seg
					JOIN mapmatched_data.viterbi_match_osm_dk_20140101 vit
					ON seg.segmentkey = vit.segmentkey
					--AND vit.ev_kwh IS NOT NULL
				) sub
			) sub2
			GROUP BY segments, segmentkey
		), single_given_before AS (
			SELECT segments, segments_driven[2] as segmentkey, avg(evs[2]) as avg_ev_per_meter
			FROM (
				SELECT 
					array_agg(segmentkey) as segments_driven, 
					sub.segments, 
					array_agg(id) as ids, 
					array_agg(ev) as evs,
					trip_id
				FROM (
					SELECT seg.*, vit.id, vit.trip_id, vit.trip_segmentno, vit.ev_kwh / vit.meters_segment as ev,
						LAG(vit.trip_segmentno, 1) OVER (
							PARTITION BY seg.segments, vit.trip_id 
							ORDER BY vit.trip_id, vit.trip_segmentno
						) as prv_segmentno
					FROM (
						SELECT distinct unnest(segments) as segmentkey, segments
						FROM superseg1
					) seg
					JOIN mapmatched_data.viterbi_match_osm_dk_20140101 vit
					ON seg.segmentkey = vit.segmentkey
					--AND vit.ev_kwh IS NOT NULL
					ORDER BY seg.segments, vit.trip_id, vit.trip_segmentno
				) sub
				WHERE (prv_segmentno = trip_segmentno - 1 OR prv_segmentno IS NULL)
				GROUP BY trip_id, segments
			) sub2
			WHERE segments_driven = segments
			GROUP BY segments, segments_driven[2]
		)
		SELECT t1.segments, t1.avg_ev_per_meter as single_ev, t2.avg_ev_per_meter as given_ev
		FROM single t1
		JOIN single_given_before t2
		ON t1.segments = t2.segments
	)
	SELECT
    FROM calc
    WHERE t1.segments = calc.segments
)
AND EXISTS (
	SELECT
	FROM experiments.rmp10_driven_supersegments_2len l2
	WHERE t1.segments = l2.segments
)