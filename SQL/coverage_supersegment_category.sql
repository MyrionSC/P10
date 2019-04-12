WITH intersections as (
	select distinct(unnest(segments)) as segmentkey
	from experiments.rmp10_intersections_v2
	UNION
	select distinct(unnest(segments)) as segmentkey
	from experiments.rmp10_t_sections
), roundabouts as (
	select distinct(segmentkey)
	from experiments.rmp10_roundabouts
), cat_changes as (
	select distinct(unnest(segments)) as segmentkey
	-- wrong table
	from experiments.rmp10_category_change_supersegs
), normal as (
	select maps.segmentkey
	from
		maps.osm_dk_20140101 maps
	WHERE
		NOT EXISTS (SELECT FROM intersections inter WHERE inter.segmentkey=maps.segmentkey) and
		NOT EXISTS (SELECT FROM roundabouts r WHERE r.segmentkey=maps.segmentkey) and
		NOT EXISTS (SELECT FROM cat_changes cc WHERE cc.segmentkey=maps.segmentkey)
)
select 
	maps.count as all_count,
	inter.count as inter_count,
	r.count as r_count,
	cc.count as cc_count,
	n.count as n_count,
	100 as all_prct,
	inter.count / maps.count::float as inter_prct,
	r.count / maps.count::float as r_prct,
	cc.count / maps.count::float as cc_prct,
	n.count / maps.count::float as n_prct
from
	(select count(*) from maps.osm_dk_20140101) maps,
	(select count(*) from intersections) inter,
	(select count(*) from roundabouts) r,
	(select count(*) from cat_changes) cc,
	(select count(*) from normal) n

