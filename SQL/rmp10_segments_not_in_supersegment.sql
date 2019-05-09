select m.segmentkey
into experiments.rmp10_segments_not_in_supersegment
from maps.osm_dk_20140101 m
where not exists(
	select distinct(unnest(segments)) as segmentkey
	from experiments.rmp10_all_supersegments
	where segmentkey=m.segmentkey
)
