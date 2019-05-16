
-- FUNCTION: public.ev_indi_superseg_updated(text)

-- DROP FUNCTION public.ev_indi_superseg_updated(text);

CREATE OR REPLACE FUNCTION public.ev_indi_superseg_updated(
	query text)
    RETURNS TABLE(segments integer[], ev double precision) 
    LANGUAGE 'plpgsql'

    COST 100
    VOLATILE 
    ROWS 1000
AS $BODY$
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
				CASE 
					WHEN e.ev_kwh_from_ev_watt IS null THEN vit.ev_kwh
					ELSE e.ev_kwh_from_ev_watt
				END AS ev_kwh
			FROM (
				SELECT unnest(segments) as segmentkey, segments
				FROM superseg
			) seg
			JOIN mapmatched_data.viterbi_match_osm_dk_20140101 vit
			ON seg.segmentkey = vit.segmentkey
			LEFT OUTER JOIN experiments.bcj_ev_watt_data e
			ON vit.id=e.id
		) sub
		GROUP BY segments, segmentkey
		ORDER BY segments, array_position(segments, segmentkey)
	) sub2
	GROUP BY segments
) sub3
WHERE segments = array_agg
';
END $BODY$;

ALTER FUNCTION public.ev_indi_superseg_updated(text)
    OWNER TO smartmi;

