
-- FUNCTION: public.ev_superseg_updated(text)

-- DROP FUNCTION public.ev_superseg_updated(text);

CREATE OR REPLACE FUNCTION public.ev_superseg_updated(
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
SELECT segments, avg(ev_kwh) / avg(meters) as target
FROM (
	SELECT
		array_agg(segmentkey) as segments_driven,
		sub.segments,
		sum(ev_kwh) as ev_kwh,
		sum(meters) as meters 
	FROM (
		SELECT 
			seg.*, 
			vit.id, 
			vit.trip_id, 
			vit.trip_segmentno, 
			CASE 
				WHEN e.ev_kwh_from_ev_watt IS null THEN vit.ev_kwh
				ELSE e.ev_kwh_from_ev_watt
			END AS ev_kwh,
			vit.meters_driven as meters,
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
		LEFT OUTER JOIN experiments.bcj_ev_watt_data e
		ON vit.id=e.id
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

ALTER FUNCTION public.ev_superseg_updated(text)
    OWNER TO smartmi;
