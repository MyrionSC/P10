----- TRAINING SPLIT
SELECT 
	atd.*
INTO experiments.rmp10_supersegments_training_data
FROM experiments.rmp10_all_trip_data atd
WHERE EXISTS (
	SELECT
	FROM (
		SELECT v.id
		FROM experiments.rmp10_training t
		JOIN experiments.rmp10_viterbi_match_osm_dk_20140101_overlap v
		ON t.id=v.origin
	) sq
	WHERE sq.id=any(atd.id_arr)
);

--ON atd.superseg_id=osm.superseg_id OR atd.segmentkey=osm.segmentkey
--JOIN dims.dimdate date_table
--ON atd.datekey = date_table.datekey
--JOIN dims.dimtime time_table
--ON atd.timekey = time_table.timekey
--JOIN dims.dimweathermeasure weather_table
--ON atd.weathermeasurekey = weather_table.weathermeasurekey;

-- training indexes
CREATE INDEX rmp10_all_supersegments_training_data_superseg_id_idx
    ON experiments.rmp10_supersegments_training_data USING btree
    (superseg_id)
    TABLESPACE pg_default;
CREATE INDEX rmp10_all_supersegments_training_data_segmentkey_idx
    ON experiments.rmp10_supersegments_training_data USING btree
    (segmentkey)
    TABLESPACE pg_default;
CREATE INDEX rmp10_all_supersegments_training_data_datekey_idx
    ON experiments.rmp10_supersegments_training_data USING btree
    (datekey)
    TABLESPACE pg_default;
CREATE INDEX rmp10_all_supersegments_training_data_timekey_idx
    ON experiments.rmp10_supersegments_training_data USING btree
    (timekey)
    TABLESPACE pg_default;
CREATE INDEX rmp10_all_supersegments_training_data_weathermeasurekey_idx
    ON experiments.rmp10_supersegments_training_data USING btree
    (weathermeasurekey)
    TABLESPACE pg_default;



----- TEST SPLIT
SELECT 
	atd.*
INTO experiments.rmp10_supersegments_test_data
FROM experiments.rmp10_all_trip_data atd
WHERE EXISTS (
	SELECT
	FROM (
		SELECT v.id
		FROM experiments.rmp10_test t
		JOIN experiments.rmp10_viterbi_match_osm_dk_20140101_overlap v
		ON t.id=v.origin
	) sq
	WHERE sq.id=any(atd.id_arr)
);

-- test indexes
CREATE INDEX rmp10_all_supersegments_test_data_superseg_id_idx
    ON experiments.rmp10_supersegments_test_data USING btree
    (superseg_id)
    TABLESPACE pg_default;
CREATE INDEX rmp10_all_supersegments_test_data_segmentkey_idx
    ON experiments.rmp10_supersegments_test_data USING btree
    (segmentkey)
    TABLESPACE pg_default;
CREATE INDEX rmp10_all_supersegments_test_data_datekey_idx
    ON experiments.rmp10_supersegments_test_data USING btree
    (datekey)
    TABLESPACE pg_default;
CREATE INDEX rmp10_all_supersegments_test_data_timekey_idx
    ON experiments.rmp10_supersegments_test_data USING btree
    (timekey)
    TABLESPACE pg_default;
CREATE INDEX rmp10_all_supersegments_test_data_weathermeasurekey_idx
    ON experiments.rmp10_supersegments_test_data USING btree
    (weathermeasurekey)
    TABLESPACE pg_default;

