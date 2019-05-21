-- final count: "13770381"

CREATE TABLE experiments.rmp10_all_trip_data
AS TABLE experiments.rmp10_all_trip_supersegments;

ALTER TABLE experiments.rmp10_all_trip_data
ADD COLUMN segmentkey integer;

--create temp indexed table holding all supersegment ids. 25445815 rows in 1 min 47 secs.
SELECT distinct(unnest(id_arr)) as id
INTO experiments.rmp10_all_trip_supersegments_id_arr_unnested
FROM experiments.rmp10_all_trip_supersegments ats;

CREATE INDEX rmp10_all_trip_supersegments_id_arr_unnested_id_btree_idx
    ON experiments.rmp10_all_trip_supersegments_id_arr_unnested USING btree
    (id)
    TABLESPACE pg_default;

-- insert. 1160312 in 1 min 13 sec
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
	FROM experiments.rmp10_all_trip_supersegments_id_arr_unnested atsids
	WHERE ol.id=atsids.id
)

--drop temp table
DROP TABLE experiments.rmp10_all_trip_supersegments_id_arr_unnested;


--indexes. 4 min 22 sec
CREATE INDEX rmp10_all_trip_data_id_arr_btree_idx
    ON experiments.rmp10_all_trip_data USING btree
    (id_arr)
    TABLESPACE pg_default;
CREATE INDEX rmp10_all_trip_data_id_arr_gin_idx
    ON experiments.rmp10_all_trip_data USING gin
    (id_arr)
    TABLESPACE pg_default;
CREATE INDEX rmp10_all_trip_data_superseg_id_idx
    ON experiments.rmp10_all_trip_data USING btree
    (superseg_id)
    TABLESPACE pg_default;
CREATE INDEX rmp10_all_trip_data_trip_id_idx
    ON experiments.rmp10_all_trip_data USING btree
    (trip_id)
    TABLESPACE pg_default;
CREATE INDEX rmp10_all_trip_data_segmentkey_idx
    ON experiments.rmp10_all_trip_data USING btree
    (segmentkey)
    TABLESPACE pg_default;

-- update with incline
-- update supersegments with incline
UPDATE experiments.rmp10_all_trip_data as atd
SET incline=inc.incline_clamped
FROM experiments.rmp10_all_supersegments_incline inc
WHERE atd.superseg_id=inc.superseg_id;

-- update single segments with incline
UPDATE experiments.rmp10_all_trip_data as atd
SET incline=inc.incline_clamped
FROM experiments.rmp10_osm_dk_20140101_overlaps_incline inc
WHERE atd.segmentkey=inc.segmentkey;











