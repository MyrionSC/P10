drop table if exists experiments.rmp10_intersections_v2;

WITH temp_intersection_cluster as (
	select *, ST_ClusterDBSCAN(ST_TRANSFORM(geom::geometry, 3857), eps := 35, minpoints := 2) over () as cid
	from (
		select *
		from experiments.rmp10_all_points
		where degree > 1
	) ssq
	),
	clusters_with_mte_4_deg as (
	select cid
	from (
		select cid, array_agg(point) as points, max(degree) as maxdeg
		from temp_intersection_cluster
		where cid is not null
		group by cid
	) t2
	where maxdeg>=4)
select *
into experiments.rmp10_intersections_v2
from (
	select c.*
	from temp_intersection_cluster c
	join clusters_with_mte_4_deg cd4
	on c.cid=cd4.cid
	union
	select *
	from temp_intersection_cluster
	where cid is null and degree>=4) t1


