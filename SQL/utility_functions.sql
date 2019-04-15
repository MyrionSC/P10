CREATE OR REPLACE FUNCTION array_uniq_sort(anyarray) RETURNS anyarray AS $$
SELECT array_agg(DISTINCT f ORDER BY f) FROM unnest($1) f;
$$ LANGUAGE sql IMMUTABLE;

CREATE OR REPLACE FUNCTION subgeoms(geom geometry)
RETURNS geometry[]
LANGUAGE 'sql'
AS $$
SELECT array_agg(ST_MakeLine(geom2, geom1)) as subgeoms
FROM (
	SELECT
		(points).geom as geom1, 
		LAG((points).geom) OVER (
			ORDER BY (points).path[1]
		) as geom2, 
		(points).path[1]
	FROM (
		SELECT ST_Dump(ST_Points(geom)) as points 
	) sub
) sub2
WHERE geom2 IS NOT NULL
$$;

CREATE OR REPLACE FUNCTION public.reduce_dim(
	anyarray)
    RETURNS SETOF anyarray 
    LANGUAGE 'plpgsql'

    COST 100
    IMMUTABLE 
    ROWS 1000
AS $BODY$
DECLARE
    s $1%TYPE;
BEGIN
    FOREACH s SLICE 1  IN ARRAY $1 LOOP
        RETURN NEXT s;
    END LOOP;
    RETURN;
END;
$BODY

CREATE OR REPLACE FUNCTION public.slice_tuples(
	anyarray)
    RETURNS SETOF anyarray 
    LANGUAGE 'plpgsql'

    COST 100
    IMMUTABLE 
    ROWS 1000
AS $BODY$
DECLARE
    s $1%TYPE;
BEGIN
    FOR i IN 2..array_length($1, 1) LOOP
        RETURN NEXT $1[i-1:i];
    END LOOP;
    RETURN;
END;
$BODY$;

CREATE FUNCTION array_sum(arr anyarray)
RETURNS anyelement
LANGUAGE 'sql'
AS $$
SELECT sum(unnest(arr))
$$;