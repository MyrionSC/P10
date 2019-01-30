-- SEQUENCE: experiments.mi904e18_test_id_seq

-- DROP SEQUENCE experiments.mi904e18_test_id_seq;

CREATE SEQUENCE experiments.mi904e18_test_id_seq;

ALTER SEQUENCE experiments.mi904e18_test_id_seq
    OWNER TO dip_readers;

GRANT ALL ON SEQUENCE experiments.mi904e18_test_id_seq TO dip_readers;

-- Table: experiments.mi904e18_test

-- DROP TABLE experiments.mi904e18_test;

CREATE TABLE experiments.mi904e18_test
(
    id bigint NOT NULL DEFAULT nextval('experiments.mi904e18_test_id_seq'::regclass),
    trip_id integer,
    trip_segmentno integer,
    vehiclekey integer,
    userkey integer,
    segmentkey integer,
    datekey integer,
    batchkey integer,
    weathermeasurekey integer,
    direction functionality.direction_driving,
    sourcekey smallint,
    timekey smallint,
    gps_points smallint,
    ev_soc smallint,
    ev_soc_trip smallint,
    speed real,
    meters_driven real,
    meters_driven_trip real,
    meters_segment real,
    meters_segment_trip real,
    seconds real,
    seconds_trip real,
    fuel_liters real,
    fuel_liters_trip real,
    fuel_liters_agg real,
    fuel_liters_agg_trip real,
    fuel_sidra real,
    fuel_sidra_trip real,
    fuel_sp real,
    fuel_sp_trip real,
    ev_kwh real,
    ev_kwh_trip real,
    primehash bigint,
    gpsdata_ids bigint[]
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE experiments.mi904e18_test
    OWNER to dip_readers;

GRANT ALL ON TABLE experiments.mi904e18_test TO dip_readers;

-- Index: ixd_datekey_mi904e18_test

-- DROP INDEX experiments.ixd_datekey_mi904e18_test;

CREATE INDEX ixd_datekey_mi904e18_test
    ON experiments.mi904e18_test USING btree
    (datekey)
    TABLESPACE pg_default;

-- Index: mi904e18_test_segmentkey_index

-- DROP INDEX experiments.mi904e18_test_segmentkey_index;

CREATE INDEX mi904e18_test_segmentkey_index
    ON experiments.mi904e18_test USING btree
    (segmentkey)
    TABLESPACE pg_default;

-- Index: mi904e18_test_segmentkey_index_asc

-- DROP INDEX experiments.mi904e18_test_segmentkey_index_asc;

CREATE INDEX mi904e18_test_segmentkey_index_asc
    ON experiments.mi904e18_test USING btree
    (segmentkey)
    TABLESPACE pg_default;

-- Index: mi904e18_test_trip_id_index

-- DROP INDEX experiments.mi904e18_test_trip_id_index;

CREATE INDEX mi904e18_test_trip_id_index
    ON experiments.mi904e18_test USING btree
    (trip_id)
    TABLESPACE pg_default;