create or replace temp view temp_intersection_cluster as (
	select *, ST_ClusterDBSCAN(ST_TRANSFORM(geom::geometry, 3857), eps := 30, minpoints := 2) over () as cid
	from experiments.rmp10_interesting_nodes
);

create or replace temp view clusters_with_mte_4_deg as (
	select cid
	from (
		select cid, array_agg(point) as points, max(degree) as maxdeg
		from temp_intersection_cluster
		where cid is not null
		group by cid
	) t2
	where maxdeg>=4
);

drop table if exists experiments.rmp10_intersections;

select *
into experiments.rmp10_intersections
from (
select c.*
from temp_intersection_cluster c
join clusters_with_mte_4_deg cd4
on c.cid=cd4.cid
union
select *
from temp_intersection_cluster
where cid is null and degree>=4) t1

