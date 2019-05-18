-- add height difference from other group
CREATE TABLE experiments.rmp10_all_supersegments_incline AS
SELECT
	superseg_id,
	(rise / run) * 100 as incline,
	degrees(atan(rise / run)) as incline_angle,
	rise as height_difference,
	sp_height = startpoint_height,
	ep_height = endpoint_height
FROM (
	SELECT 
		alls.superseg_id,
		ep.height - sp.height as rise,
		alls.meters as run,
		sp.height as sp_height,
		ep.height as ep_height
	FROM experiments.rmp10_all_supersegments alls
	JOIN experiments.rmp10_osm_dk_20140101_overlaps_points sp
	ON sp.point = alls.startpoint
	JOIN experiments.rmp10_osm_dk_20140101_overlaps_points ep
	ON sp.point = alls.endpoint
) sub;