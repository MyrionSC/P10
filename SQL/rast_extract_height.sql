-- get raster values at particular postgis geometry points
-- the srid of your geometry should be same as for your raster
SELECT rid, rast, rast::geometry as geo, ST_AsText(rast::geometry) as corners, ST_Value(rast, 1, x,y) As height, x ,y
FROM experiments.heightmap
CROSS JOIN generate_series(1, 13) As x 
CROSS JOIN generate_series(1, 7) As y
WHERE rid=2;
