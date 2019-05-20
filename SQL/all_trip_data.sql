--CREATE TABLE experiments.rmp10_all_trip_data
--AS TABLE experiments.rmp10_all_trip_supersegments;

ALTER TABLE experiments.rmp10_all_trip_data
ADD COLUMN segmentkey integer;

INSERT INTO experiments.rmp10_all_trip_data
SELECT
	null,
	trip_id,
	trip_segmentno,
	trip_segmentno,
	null,
	meters_segment,
	meters_driven,
	seconds,
	null,
	ev_kwh * 1000,
	datekey,
	timekey,
	weathermeasurekey,
	ARRAY[id],
	segmentkey
FROM experiments.rmp10_viterbi_match_osm_dk_20140101_overlap ol
WHERE NOT EXISTS (
	SELECT
	FROM experiments.rmp10_all_trip_supersegments ats
	WHERE ol.id=any(ats.id_arr)
)
	