--DROP FUNCTION experiments.rmp10_intersection_supersegment_internal_path(integer,integer,bigint);

CREATE OR REPLACE FUNCTION experiments.rmp10_intersection_supersegment_internal_path (entry_seg_key integer, exit_seg_key integer, cluster_id bigint)
	   RETURNS integer[]
	   LANGUAGE 'sql'
AS $$
	WITH RECURSIVE internal_path(curr_point, internalseg_entrypoint, internalseg_exitpoint, path, is_done, i) AS (
		WITH internal_segs AS (
			SELECT *
			FROM experiments.rmp10_intersection_segment_types ist
			WHERE segtype='Internal' and cid=cluster_id --cluser_id
		), internalseg_entrypoint AS (
			select
				distinct(CASE 
					WHEN ms.startpoint=isegs.startpoint or ms.startpoint=isegs.endpoint THEN ms.startpoint
					ELSE ms.endpoint
				END) AS point
			from internal_segs isegs
			join maps.osm_dk_20140101 ms
			on ms.segmentkey=entry_seg_key --entry_seg_key
		), internalseg_exitpoint AS (
			select
				distinct(CASE 
					WHEN ms.startpoint=isegs.startpoint or ms.startpoint=isegs.endpoint THEN ms.startpoint
					ELSE ms.endpoint
				END) AS point
			from internal_segs isegs
			join maps.osm_dk_20140101 ms
			on ms.segmentkey=exit_seg_key --exit_seg_key
		)
		select
			entrypoint.point as curr_point,
			entrypoint.point as internalseg_entrypoint,
			exitpoint.point as internalseg_exitpoint,
			array[]::integer[] as path,
			entrypoint.point=exitpoint.point AS is_done,
			0 as i
		from
			internalseg_entrypoint entrypoint,
			internalseg_exitpoint exitpoint
		UNION ALL
		select 
			nxt.endpoint as curr_point,
			prv.internalseg_entrypoint,
			prv.internalseg_exitpoint,
			prv.path || nxt.segmentkey,
			nxt.endpoint=prv.internalseg_exitpoint or 
				nxt.startpoint=prv.internalseg_exitpoint as is_done,
			prv.i+1
		from internal_segs nxt
		join internal_path prv
		on 
			(prv.curr_point = nxt.startpoint OR
			 nxt.segtype = 'Both' and prv.curr_point = nxt.endpoint) AND
			prv.i<=5 
	)
	select path
	from internal_path
	where is_done
	order by i
	limit 1
$$;
