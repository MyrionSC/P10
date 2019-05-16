-- FUNCTION: public.ev_superseg_indi(text)

-- DROP FUNCTION public.ev_superseg_indi(text);

CREATE OR REPLACE FUNCTION public.ev_superseg_indi(
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
SELECT segments, target / meters as target
FROM (
	SELECT
		array_agg(segmentkey) as segments_driven,
		sub.segments,
		sum(target) as target,
		sum(meters) as meters
	FROM (
		SELECT 
			seg.segmentkey,
			seg.segments,
			avg(vit.ev_kwh)::double precision as target,
			avg(vit.meters_driven) as meters
		FROM (
			SELECT unnest(segments) as segmentkey, segments
			FROM superseg
		) seg
		JOIN mapmatched_data.viterbi_match_osm_dk_20140101 vit
		ON seg.segmentkey = vit.segmentkey
		GROUP BY seg.segments, seg.segmentkey
		ORDER BY seg.segments, array_position(seg.segments, seg.segmentkey)
	) sub
	GROUP BY segments
) sub2
WHERE segments = segments_driven
';
END $BODY$;

ALTER FUNCTION public.ev_superseg_indi(text)
    OWNER TO smartmi;

