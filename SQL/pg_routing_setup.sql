CREATE TABLE maps.routing AS
SELECT 
	segmentkey, 
	startpoint, 
	endpoint, 
	segmentgeo::geometry as segmentgeom
FROM maps.osm_dk_20140101;

CREATE TABLE maps.routing2 AS
SELECT 
	segmentkey, 
	startpoint, 
	endpoint, 
	segmentgeo::geometry as segmentgeom
FROM maps.osm_dk_20140101 osm1
UNION
SELECT 
	segmentkey, 
	endpoint as startpoint, 
	startpoint as endpoint, 
	segmentgeo::geometry as segmentgeom
FROM maps.osm_dk_20140101
WHERE direction='BOTH';

SELECT pgr_createTopology('maps.routing', 0.001, 'segmentgeom', 'segmentkey', 'startpoint', 'endpoint');
SELECT pgr_createTopology('maps.routing2', 0.001, 'segmentgeom', 'segmentkey', 'startpoint', 'endpoint');

ALTER TABLE maps.routing
ADD COLUMN length float;

UPDATE maps.routing
SET length = maps.osm_dk_20140101.meters
FROM maps.osm_dk_20140101
WHERE maps.routing.segmentkey = maps.osm_dk_20140101.segmentkey;

ALTER TABLE maps.routing2
ADD COLUMN length float;

UPDATE maps.routing2
SET length = maps.osm_dk_20140101.meters
FROM maps.osm_dk_20140101
WHERE maps.routing2.segmentkey = maps.osm_dk_20140101.segmentkey;
