CREATE FUNCTION rmp10_clamp(
	val double precision, 
	lower_bound double precision, 
	upper_bound double precision
)
RETURNS double precision
LANGUAGE 'sql'
AS $$
	SELECT GREATEST(lower_bound, LEAST(upper_bound, val))
$$