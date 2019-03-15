select distinct(trip_id)
from 
	experiments.rmp10_aalborg_start_trips aaltrips,
	(select *
		from experiments.rmp10_aalborg_routing rout
		where rout.endpoint=any(array[23060, 23061, 359483, 422928]) or
		rout.startpoint=any(array[23060, 23061, 359483, 422928])
	) intersegs
where aaltrips.segmentkey=intersegs.segmentkey
