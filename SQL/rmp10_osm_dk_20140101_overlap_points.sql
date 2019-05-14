CREATE TABLE experiments.rmp10_osm_dk_20140101_overlaps_points AS
SELECT DISTINCT 
	startpoint as point, 
	ST_Startpoint(segmentgeo::geometry)::geography as geo
FROM experiments.rmp10_osm_dk_20140101_overlaps
UNION
SELECT DISTINCT 
	endpoint as point, 
	ST_Endpoint(segmentgeo::geometry)::geography as geo
FROM experiments.rmp10_osm_dk_20140101_overlaps

CREATE INDEX rmp10_osm_dk_20140101_points_geo_idx
    ON experiments.rmp10_osm_dk_20140101_overlaps_points USING gist
    (geo)
    WITH (FILLFACTOR=100)
    TABLESPACE pg_default;

CREATE INDEX rmp10_osm_dk_20140101_points_geo_25832_index
    ON experiments.rmp10_osm_dk_20140101_overlaps_points USING btree
    (st_transform(geo::geometry, 25832))
    TABLESPACE pg_default;
	
CREATE INDEX rmp10_osm_dk_20140101_points_point_idx
    ON experiments.rmp10_osm_dk_20140101_overlaps_points USING btree
    (point)
    TABLESPACE pg_default;

ALTER TABLE experiments.rmp10_osm_dk_20140101_overlaps_points
ADD COLUMN traffic_lights boolean;

UPDATE experiments.rmp10_osm_dk_20140101_overlaps_points op
SET traffic_lights = ss.traffic_lights
FROM experiments.rmp10_osm_points ss
WHERE op.point = ss.point;

UPDATE experiments.rmp10_osm_dk_20140101_overlaps_points op
SET traffic_lights = False
WHERE traffic_lights is null;

ALTER TABLE experiments.rmp10_osm_dk_20140101_overlaps_points
ADD COLUMN height double precision;

UPDATE experiments.rmp10_osm_dk_20140101_overlaps_points op
SET height = h
FROM (
    SELECT p.point, ST_NearestValue(r.rast, p.geo::geometry) as h
    FROM experiments.bcj_heightmapbridge r
    JOIN experiments.rmp10_osm_dk_20140101_overlaps_points p
    ON ST_Intersects(p.geo::geometry, r.rast)
) sub
WHERE sub.point = op.point;