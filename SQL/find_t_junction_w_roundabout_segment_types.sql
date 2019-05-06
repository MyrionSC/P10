create OR REPLACE view experiments.rmp10_t_junction_w_roundabouts_segment_types as (
	with section_segs as (
		select point, unnest(segments) as segmentkey
		from experiments.rmp10_t_junction_w_roundabout
	)
	select
		ss.point,
		CASE 
			when m.direction='BOTH' Then 'Both'
			When m.startpoint=ss.point and not m.endpoint=ss.point Then 'Out'
			When not m.startpoint=ss.point and m.endpoint=ss.point Then 'In'
		END as segtype,
		m.*
	from section_segs ss
	join maps.osm_dk_20140101 m
	on ss.segmentkey=m.segmentkey
);


