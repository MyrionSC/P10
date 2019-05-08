--ALTER TABLE experiments.rmp10_all_supersegments
--ADD COLUMN height_difference double precision;

UPDATE experiments.rmp10_all_supersegments as sups
SET height_difference=sssq.hd
FROM (
	select segments, type, sum(height_difference) as hd
	from (
		select sq.*, inc.height_difference
		from (
			select unnest(segments) as segment, segments, type
			from experiments.rmp10_all_supersegments
		) sq
		join experiments.bcj_incline inc
		on sq.segment = inc.segmentkey
	) ssq
	group by segments, type
) sssq
WHERE sups.segments=sssq.segments and sups.type=sssq.type

