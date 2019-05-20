-- add height difference from other group
CREATE TABLE experiments.rmp10_all_supersegments_incline AS
SELECT
	superseg_id,
	(rise / run) * 100 as incline,
	degrees(atan(rise / run)) as incline_angle,
	rise as height_difference,
	sp_height as startpoint_height,
	ep_height as endpoint_height
FROM (
	SELECT 
		alls.superseg_id,
		ep.height - sp.height as rise,
		NULLIF(alls.meters, 0) as run,
		sp.height as sp_height,
		ep.height as ep_height
	FROM experiments.rmp10_all_supersegments alls
	JOIN experiments.rmp10_osm_dk_20140101_overlaps_points sp
	ON sp.point = alls.startpoint
	JOIN experiments.rmp10_osm_dk_20140101_overlaps_points ep
	ON ep.point = alls.endpoint
) sub;

ALTER TABLE experiments.rmp10_all_supersegments_incline
ADD COLUMN incline_clamped double precision;

UPDATE experiments.rmp10_all_supersegments_incline
SET incline_clamped = rmp10_clamp(incline, -10, 10);

CREATE INDEX rmp10_all_supersegments_incline_superseg_id_idx 
ON experiments.rmp10_all_supersegments_incline
USING btree(superseg_id);