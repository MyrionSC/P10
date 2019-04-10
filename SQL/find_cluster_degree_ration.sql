select *
from (
	WITH deg_cat_table AS (
		select 
			cid, 
			CASE 
				WHEN degree<4 THEN 'lt4_degs'
				ELSE 'mte4_degs'
			END AS degree_cats,
			count(*) as c, 
			st_union(geom::geometry) as geom
		from experiments.rmp10_intersections_v2
		where cid is not null
		group by 
			cid, 
			CASE 
				WHEN degree<4 THEN 'lt4_degs'
				ELSE 'mte4_degs'
			END
		order by cid
	)
select t1.cid, t1.c as mte4_degs_count, t2.c as lt4_degs_count, t1.c / t2.c::float as ratio, st_union(t1.geom, t2.geom)
from deg_cat_table t1
join deg_cat_table t2
on t1.cid=t2.cid and t1.degree_cats='mte4_degs' and t2.degree_cats='lt4_degs'
) sq
where ratio<=0.25
