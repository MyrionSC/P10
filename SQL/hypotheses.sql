-- Hypotese 1
--DROP TABLE IF EXISTS experiments.rmp10_diff_ways_ev_supersegs;
--CREATE TABLE experiments.rmp10_diff_ways_ev_supersegs AS
WITH superseg1 AS (
	SELECT superseg_id, segments
	FROM experiments.rmp10_driven_supersegments_2len_new
), superseg2 AS (
	SELECT superseg_id, ARRAY[segments[2], segments[1]] as segments
	FROM experiments.rmp10_driven_supersegments_2len_new
), one_way AS (
	SELECT superseg_id, segments, avg(ev_per_meter) as avg_ev_per_meter
	FROM (
		SELECT 
			superseg_id,
			array_agg(segmentkey) as segments_driven, 
			sub.segments, 
			array_agg(id) as ids, 
			avg(ev_kwh) as ev_per_meter,
			trip_id
		FROM (
			SELECT seg.*, vit.id, vit.trip_id, vit.trip_segmentno, vit.ev_kwh / vit.meters_segment as ev_kwh,
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
		) sub
		WHERE (prv_segmentno = trip_segmentno - 1 OR prv_segmentno IS NULL)
		GROUP BY superseg_id, trip_id, segments
	) sub2
	WHERE segments_driven = segments
	GROUP BY superseg_id, segments
	ORDER BY superseg_id
), other_way AS (
	SELECT superseg_id, ARRAY[segments[2], segments[1]] as segments, avg(ev_per_meter) as avg_ev_per_meter
	FROM (
		SELECT 
			superseg_id,
			array_agg(segmentkey) as segments_driven, 
			sub.segments, 
			array_agg(id) as ids, 
			avg(ev_kwh) as ev_per_meter,
			trip_id
		FROM (
			SELECT seg.*, vit.id, vit.trip_id, vit.trip_segmentno, vit.ev_kwh / vit.meters_segment as ev_kwh,
				LAG(vit.trip_segmentno, 1) OVER (
					PARTITION BY seg.superseg_id, vit.trip_id 
					ORDER BY seg.superseg_id, vit.trip_id, vit.trip_segmentno
				) as prv_segmentno
			FROM (
				SELECT distinct superseg_id, unnest(segments) as segmentkey, segments
				FROM superseg2
			) seg
			JOIN mapmatched_data.viterbi_match_osm_dk_20140101 vit
			ON seg.segmentkey = vit.segmentkey
			AND vit.ev_kwh IS NOT NULL
		) sub
		WHERE (prv_segmentno = trip_segmentno - 1 OR prv_segmentno IS NULL)
		GROUP BY superseg_id, trip_id, segments
	) sub2
	WHERE segments_driven = segments
	GROUP BY superseg_id, segments
	ORDER BY superseg_id
)
SELECT t1.superseg_id, t1.segments, t1.avg_ev_per_meter as one_ev, t2.avg_ev_per_meter as other_ev
FROM one_way t1
JOIN other_way t2
ON t1.superseg_id = t2.superseg_id

-- Hypotese 2
--DROP TABLE IF EXISTS experiments.rmp10_given_last_ev_supersegs;
--CREATE TABLE experiments.rmp10_given_last_ev_supersegs AS
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
ON t1.superseg_id = t2.superseg_id