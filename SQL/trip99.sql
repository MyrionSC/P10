CREATE VIEW experiments.rmp10_trip99_supersegs AS 
SELECT trip_segmentno, superseg as segments
FROM (
	SELECT 
		trip_id, 
		ARRAY[
			segmentkey, 
			LEAD(segmentkey, 1) OVER (ORDER BY trip_segmentno)
		] as superseg, 
		trip_segmentno
	FROM mapmatched_data.viterbi_match_osm_dk_20140101 vit
	WHERE trip_id = 99
	ORDER BY trip_segmentno
) sub
WHERE superseg[2] IS NOT NULL

WITH superseg AS (
		SELECT * FROM experiments.rmp10_trip99_supersegs
), trips_on_99 AS (
	SELECT superseg_id, segments, avg(evs[1] + evs[2]) as average_sums
	FROM (
		SELECT superseg_id, segments, ids, evs, trip_id
		FROM (
			SELECT 
				superseg_id,
				array_agg(segmentkey) as segments_driven, 
				sub.segments, 
				array_agg(id) as ids, 
				array_agg(ev_kwh) as evs,
				trip_id
			FROM (
				SELECT seg.*, vit.id, vit.trip_id, vit.trip_segmentno, vit.ev_kwh,
					LAG(vit.trip_segmentno, 1) OVER (
						PARTITION BY seg.superseg_id, vit.trip_id 
						ORDER BY seg.superseg_id, vit.trip_id, vit.trip_segmentno
					) as prv_segmentno
				FROM (
					SELECT distinct trip_segmentno as superseg_id, unnest(segments) as segmentkey, segments
					FROM superseg
				) seg
				JOIN mapmatched_data.viterbi_match_osm_dk_20140101 vit
				ON seg.segmentkey = vit.segmentkey
				ORDER BY seg.superseg_id, vit.trip_id, vit.trip_segmentno
			) sub
			WHERE (prv_segmentno = trip_segmentno - 1 OR prv_segmentno IS NULL)
			GROUP BY superseg_id, trip_id, segments
		) sub2
		WHERE segments_driven = segments
	) sub3
	GROUP BY superseg_id, segments
	ORDER BY superseg_id
), totals_on_99 AS (
	SELECT segmentkey, avg(ev_kwh) as avg_ev
	FROM (
		SELECT DISTINCT
			seg.segmentkey,
			id, 
			ev_kwh,
			trip_id,
			trip_segmentno
		FROM (
			SELECT distinct trip_segmentno as superseg_id, unnest(segments) as segmentkey, segments
			FROM superseg
		) seg
		JOIN mapmatched_data.viterbi_match_osm_dk_20140101 vit
		ON seg.segmentkey = vit.segmentkey
		ORDER BY trip_id, trip_segmentno
	) sub1
GROUP BY segmentkey
)
SELECT trips_on_99.*, totals_on_99.sum_averages, ST_Union(osm1.segmentgeo::geometry, osm2.segmentgeo::geometry) as geo
FROM trips_on_99
JOIN totals_on_99
ON trips_on_99.superseg_id = totals_on_99.superseg_id
JOIN maps.osm_dk_20140101 osm1
ON osm1.segmentkey = trips_on_99.segments[1]
JOIN maps.osm_dk_20140101 osm2
ON osm2.segmentkey = trips_on_99.segments[2]					   

WITH superseg AS (
		SELECT * FROM experiments.rmp10_trip99_supersegs
), trips_on_99 AS (
	SELECT superseg_id, segments, avg(evs[1] + evs[2]) as average_sums
	FROM (
		SELECT superseg_id, segments, ids, evs, trip_id
		FROM (
			SELECT 
				superseg_id,
				array_agg(segmentkey) as segments_driven, 
				sub.segments, 
				array_agg(id) as ids, 
				array_agg(ev_kwh) as evs,
				trip_id
			FROM (
				SELECT seg.*, vit.id, vit.trip_id, vit.trip_segmentno, vit.ev_kwh,
					LAG(vit.trip_segmentno, 1) OVER (
						PARTITION BY seg.superseg_id, vit.trip_id 
						ORDER BY seg.superseg_id, vit.trip_id, vit.trip_segmentno
					) as prv_segmentno
				FROM (
					SELECT distinct trip_segmentno as superseg_id, unnest(segments) as segmentkey, segments
					FROM superseg
				) seg
				JOIN mapmatched_data.viterbi_match_osm_dk_20140101 vit
				ON seg.segmentkey = vit.segmentkey
				ORDER BY seg.superseg_id, vit.trip_id, vit.trip_segmentno
			) sub
			WHERE (prv_segmentno = trip_segmentno - 1 OR prv_segmentno IS NULL)
			GROUP BY superseg_id, trip_id, segments
		) sub2
		WHERE segments_driven = segments
	) sub3
	GROUP BY superseg_id, segments
	ORDER BY superseg_id
), totals_on_99 AS (
	SELECT segmentkey, avg(ev_kwh) as avg_ev
	FROM (
		SELECT DISTINCT
			seg.segmentkey,
			id, 
			ev_kwh,
			trip_id,
			trip_segmentno
		FROM (
			SELECT distinct trip_segmentno as superseg_id, unnest(segments) as segmentkey, segments
			FROM superseg
		) seg
		JOIN mapmatched_data.viterbi_match_osm_dk_20140101 vit
		ON seg.segmentkey = vit.segmentkey
		ORDER BY trip_id, trip_segmentno
	) sub1
GROUP BY segmentkey
)
SELECT trips_on_99.*, totals_on_99.sum_averages, ST_Union(osm1.segmentgeo::geometry, osm2.segmentgeo::geometry) as geo
FROM trips_on_99
JOIN totals_on_99
ON trips_on_99.superseg_id = totals_on_99.superseg_id
JOIN maps.osm_dk_20140101 osm1
ON osm1.segmentkey = trips_on_99.segments[1]
JOIN maps.osm_dk_20140101 osm2
ON osm2.segmentkey = trips_on_99.segments[2]					   

WITH superseg AS (
		SELECT * FROM experiments.rmp10_trip99_supersegs
), trips_on_99 AS (
	SELECT segmentkey, avg(ev_kwh) as avg_ev
	FROM (
		SELECT DISTINCT
			segmentkey,
			id, 
			ev_kwh,
			trip_id,
			trip_segmentno
		FROM (
			SELECT seg.*, vit.id, vit.trip_id, vit.trip_segmentno, vit.ev_kwh,
				LAG(vit.trip_segmentno, 1) OVER (
					PARTITION BY seg.superseg_id, vit.trip_id 
					ORDER BY seg.superseg_id, vit.trip_id, vit.trip_segmentno
				) as prv_segmentno
			FROM (
				SELECT distinct trip_segmentno as superseg_id, unnest(segments) as segmentkey, segments
				FROM superseg
			) seg
			JOIN mapmatched_data.viterbi_match_osm_dk_20140101 vit
			ON seg.segmentkey = vit.segmentkey
			ORDER BY seg.superseg_id, vit.trip_id, vit.trip_segmentno
		) sub
		WHERE trip_segmentno = prv_segmentno + 1
		OR prv_segmentno IS NULL
		ORDER BY trip_id, trip_segmentno
	) sub1
	GROUP BY segmentkey
), totals_on_99 AS (
	SELECT segmentkey, avg(ev_kwh) as avg_ev
	FROM (
		SELECT DISTINCT
			seg.segmentkey,
			id, 
			ev_kwh,
			trip_id,
			trip_segmentno
		FROM (
			SELECT distinct trip_segmentno as superseg_id, unnest(segments) as segmentkey, segments
			FROM superseg
		) seg
		JOIN mapmatched_data.viterbi_match_osm_dk_20140101 vit
		ON seg.segmentkey = vit.segmentkey
		ORDER BY trip_id, trip_segmentno
	) sub1
	GROUP BY segmentkey
)
SELECT 
	99 as trip_id,
	sum(totals_ev) as tot_indiviual, 
	sum(avg_ev) as tot_sequence, 
	sum(diff) as tot_diff,
	sum(totals_ev) - sum(avg_ev) as diff_tot
FROM (
	SELECT
		trips_on_99.*, 
		totals_on_99.avg_ev as totals_ev,
		abs(totals_on_99.avg_ev - trips_on_99.avg_ev) as diff,
		abs((totals_on_99.avg_ev - trips_on_99.avg_ev) / totals_on_99.avg_ev) as percent_diff,
		osm.segmentgeo::geometry as geo
	FROM trips_on_99
	JOIN totals_on_99
	ON trips_on_99.segmentkey = totals_on_99.segmentkey
	JOIN maps.osm_dk_20140101 osm
	ON osm.segmentkey = trips_on_99.segmentkey
) sub

WITH segments AS (
	SELECT distinct trip_segmentno, osm.segmentkey, meters_segment, osm.category
	FROM mapmatched_data.viterbi_match_osm_dk_20140101 vit
	JOIN maps.osm_dk_20140101 osm
	ON trip_id = 99
	AND vit.segmentkey = osm.segmentkey
), t1 as (
	SELECT trip_segmentno, segmentkey, meters_segment * baseline.avg_ev as expected
	FROM segments segs
	JOIN experiments.rmp10_avg_ev_per_meter_per_category as baseline
	ON segs.category = baseline.category
	ORDER BY trip_segmentno
), t2 as (
	SELECT 
		id,
		segmentkey,
		avg(ev_kwh) as actual
	FROM (
		SELECT 
			segs.trip_segmentno as id, 
			segs.segmentkey, 
			vit.trip_id, 
			vit.trip_segmentno,
			vit.ev_kwh,
			LAG(vit.trip_segmentno) OVER (PARTITION BY vit.trip_id ORDER BY vit.trip_id, segs.trip_segmentno) as prev_no
		FROM segments segs
		JOIN mapmatched_data.viterbi_match_osm_dk_20140101 vit
		ON segs.segmentkey = vit.segmentkey
		ORDER BY vit.trip_id, vit.trip_segmentno
	) sub
	WHERE trip_segmentno = prev_no + 1
	OR prev_no IS NULL
	GROUP BY id, segmentkey
	ORDER BY id
)
SELECT 
	sum(expected) as expected, 
	sum(actual) as actual, 
	abs(sum(expected) - sum(actual)) sum_diff, 
	sum(abs(expected - actual)) diff_sum
FROM (
	SELECT t1.trip_segmentno, t1.segmentkey, expected, actual, segmentgeo::geometry
	FROM t1
	JOIN t2
	ON t1.segmentkey = t2.segmentkey
	JOIN maps.osm_dk_20140101 osm
	ON t1.segmentkey = osm.segmentkey
) sub