DROP TABLE IF EXISTS experiments.rmp10_driven_supersegments_2len;

CREATE TABLE experiments.rmp10_driven_supersegments_2len (
	superseg_id BIGSERIAL,
	segments integer[]
);

INSERT INTO experiments.rmp10_driven_supersegments_2len (segments)
SELECT ARRAY[osm1.segmentkey, osm2.segmentkey] as segments
FROM experiments.rmp10_osm_dk_20140101_driven osm1
JOIN experiments.rmp10_osm_dk_20140101_driven osm2
ON osm1.endpoint = ANY(ARRAY[osm2.startpoint, osm2.endpoint])
OR osm1.startpoint = ANY(ARRAY[osm2.startpoint, osm2.endpoint]);

DROP TABLE IF EXISTS experiments.rmp10_diff_ways_ev_supersegs;
CREATE TABLE experiments.rmp10_diff_ways_ev_supersegs AS
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
ON t1.superseg_id = t2.superseg_id;

CREATE TABLE experiments.rmp10_roundabout_supersegs_2len (
	superseg_id bigserial,
	segments integer[]
);

INSERT INTO experiments.rmp10_roundabout_supersegs_2len (segments)
WITH seg AS (
	SELECT distinct segmentkey FROM experiments.rmp10_roundabouts
)
SELECT 
	distinct ARRAY[prv_seg, seg.segmentkey] as segments
FROM seg
JOIN (
	SELECT *, LAG(segmentkey, 1) OVER (
		PARTITION BY trip_id ORDER BY trip_id, trip_segmentno
	) as prv_seg, LAG(trip_segmentno, 1) OVER (
		PARTITION BY trip_id ORDER BY trip_id, trip_segmentno
	) as prv_no
	FROM mapmatched_data.viterbi_match_osm_dk_20140101
) vit
ON seg.segmentkey = vit.segmentkey
AND ev_kwh IS NOT NULL
AND prv_no = trip_segmentno - 1;

SELECT 
	segmentkey, 
	ind.category, 
	ind.avg_meter as indi_avg, 
	catavg.avg_ev as tot_avg, 
	abs(catavg.avg_ev - ind.avg_meter) as absolute_error,
	abs((catavg.avg_ev - ind.avg_meter) / catavg.avg_ev) as percent_error
FROM (
	SELECT osm.segmentkey, category, avg(ev_kwh / meters_segment) as avg_meter
	FROM maps.osm_dk_20140101 osm
	JOIN mapmatched_data.viterbi_match_osm_dk_20140101 vit
	ON osm.segmentkey = vit.segmentkey
	GROUP BY osm.segmentkey, category
) ind
JOIN experiments.rmp10_avg_ev_per_meter_per_category catavg
ON ind.category = catavg.category;

CREATE VIEW experiments.rmp10_special_supersegs AS
SELECT superseg_id, segments
FROM experiments.rmp10_driven_supersegments_2len l2
WHERE EXISTS (
	SELECT
	FROM experiments.rmp10_interesting_nodes ino
	WHERE ino.point=l2.point
)

ALTER TABLE experiments.rmp10_driven_supersegments_2len
ADD COLUMN point integer;

UPDATE experiments.rmp10_driven_supersegments_2len l2
SET point = news.point[1]
FROM (
	SELECT l1.superseg_id, l1.segments, 
	array_intersect(
		ARRAY[osm1.startpoint, osm1.endpoint], 
		ARRAY[osm2.startpoint, osm2.endpoint]
	) as point
	FROM experiments.rmp10_driven_supersegments_2len l1
	JOIN maps.osm_dk_20140101 osm1
	ON l1.segments[1] = osm1.segmentkey
	JOIN maps.osm_dk_20140101 osm2
	ON l1.segments[2] = osm2.segmentkey
) news
WHERE news.segments = l2.segments;

CREATE VIEW experiments.rmp10_complex_intersections_supersegment_2len AS
SELECT cid_w_single, in_segkey, out_segkey, slice_tuples(supersegment) as segments
FROM experiments.rmp10_intersection_supersegments_v2
WHERE cid_w_single <= 27497;