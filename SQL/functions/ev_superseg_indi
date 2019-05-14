
-- FUNCTION: public.ev_indi_superseg(text)

-- DROP FUNCTION public.ev_indi_superseg(text);

CREATE OR REPLACE FUNCTION public.ev_indi_superseg(
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
END $BODY$;

ALTER FUNCTION public.ev_indi_superseg(text)
    OWNER TO smartmi;
