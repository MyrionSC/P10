WITH superseg AS (
	SELECT * FROM experiments.rmp10_roundabout_supersegments
)
SELECT superseg_id, segments, ids, speeds, trip_id
FROM (
	SELECT 
		superseg_id,
		array_agg(segmentkey) as segments_driven, 
		sub.segments, 
		array_agg(id) as ids, 
		array_agg(speed) as speeds,
		trip_id
	FROM (
		SELECT seg.*, vit.id, vit.trip_id, vit.trip_segmentno, vit.speed,
			LAG(vit.trip_segmentno, 1) OVER (
				PARTITION BY seg.superseg_id, vit.trip_id 
				ORDER BY seg.superseg_id, vit.trip_id, vit.trip_segmentno
			) as prv_segmentno
		FROM (
			SELECT distinct superseg_id, roundabout_id, unnest(segments) as segmentkey, segments
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