select *
into experiments.rmp10_segments_not_in_supersegment
from maps.osm_dk_20140101 m
where not exists(
	select 
	from (
		select distinct(unnest(segments)) as segmentkey
		from experiments.rmp10_all_supersegments
	) sq
	where sq.segmentkey=m.segmentkey
)

CREATE INDEX rmp10_segments_not_in_supersegment_segmentkey_idx
    ON experiments.rmp10_segments_not_in_supersegment USING btree
    (segmentkey)
    TABLESPACE pg_default;
