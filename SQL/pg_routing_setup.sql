CREATE TABLE maps.routing AS
SELECT segmentkey, startpoint, endpoint, segmentgeo::geometry as segmentgeom
FROM maps.osm_dk_20140101;

SELECT pgr_createTopology('maps.routing', 0.001, 'segmentgeom', 'segmentkey', 'startpoint', 'endpoint');