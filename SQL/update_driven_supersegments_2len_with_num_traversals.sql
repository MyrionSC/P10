alter table experiments.rmp10_driven_supersegments_2len
add column num_traversals bigint;

update experiments.rmp10_driven_supersegments_2len as outer_ds
set num_traversals=sq.num_traversals
from (
	select
		superseg_id,
		count(*) as num_traversals
	from experiments.rmp10_driven_supersegments_2len ds
	join mapmatched_data.viterbi_match_osm_dk_20140101 s1
	on ds.segments[1]=s1.segmentkey
	join mapmatched_data.viterbi_match_osm_dk_20140101 s2
	on 
		ds.segments[2]=s2.segmentkey and
		s1.trip_id=s2.trip_id and
		s1.trip_segmentno=s2.trip_segmentno - 1
	group by superseg_id
) sq
where outer_ds.superseg_id=sq.superseg_id;


