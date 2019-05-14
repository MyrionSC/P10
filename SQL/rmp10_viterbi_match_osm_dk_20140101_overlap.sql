CREATE TABLE experiments.rmp10_viterbi_match_osm_dk_20140101_overlap
AS TABLE mapmatched_data.viterbi_match_osm_dk_20140101
WITH NO DATA;

ALTER TABLE experiments.rmp10_viterbi_match_osm_dk_20140101_overlap
ADD COLUMN origin bigint;

CREATE SEQUENCE experiments.rmp10_overlap_vit_id
START 14473007;

INSERT INTO experiments.rmp10_viterbi_match_osm_dk_20140101_overlap (id, trip_id, trip_segmentno, segmentkey, direction, interseg_no, origin)
SELECT 
	nextval('experiments.rmp10_overlap_vit_id'), 
	trip_id, 
	trip_segmentno,
	segmentkey,
	direction,
	interseg_no,
	id
FROM (
	SELECT os.segmentkey, vit.trip_id, vit.trip_segmentno, vit.direction, os.interseg_no, vit.id
	FROM mapmatched_data.viterbi_match_osm_dk_20140101 vit
	JOIN experiments.rmp10_osm_dk_20140101_overlaps os
	ON vit.segmentkey = os.origin
	ORDER BY trip_id, trip_segmentno, interseg_no
) ss;

INSERT INTO experiments.rmp10_viterbi_match_osm_dk_20140101_overlap (id, trip_id, trip_segmentno, segmentkey, direction, interseg_no, origin)
SELECT
	id,
	trip_id,
	trip_segmentno,
	segmentkey,
	direction,
	1,
	id
FROM mapmatched_data.viterbi_match_osm_dk_20140101 vit
WHERE NOT EXISTS (
	SELECT
	FROM experiments.rmp10_viterbi_match_osm_dk_20140101_overlap os
	WHERE os.origin = vit.id
);

ALTER TABLE experiments.rmp10_osm_dk_20140101_overlaps
ADD COLUMN interseg_no integer;

UPDATE experiments.rmp10_osm_dk_20140101_overlaps
SET interseg_no = CASE WHEN startpoint < endpoint THEN 1 ELSE 2 END;

UPDATE experiments.rmp10_viterbi_match_osm_dk_20140101_overlap
SET interseg_no = CASE WHEN direction = 'FORWARD' 
					   THEN interseg_no
					   ELSE CASE WHEN interseg_no = 1 THEN 2
					    		 ELSE 1 END
				  END;
			  
UPDATE experiments.rmp10_viterbi_match_osm_dk_20140101_overlap t1
SET trip_segmentno = n
FROM (
	SELECT 
		id,
		row_number() OVER (
			PARTITION BY trip_id 
			ORDER BY trip_id, trip_segmentno, interseg_no
		) as n
	FROM experiments.rmp10_viterbi_match_osm_dk_20140101_overlap 
) t2
WHERE t1.id = t2.id;

UPDATE experiments.rmp10_viterbi_match_osm_dk_20140101_overlap os
SET ev_soc = CASE WHEN interseg_no = 1 THEN floor(vit.ev_soc::real / 2)::smallint ELSE ceil(vit.ev_soc::real / 2)::smallint END
FROM mapmatched_data.viterbi_match_osm_dk_20140101 vit
WHERE os.id != os.origin
AND vit.id = os.origin;

UPDATE experiments.rmp10_viterbi_match_osm_dk_20140101_overlap
SET ev_soc = NULL
WHERE ev_soc = 0;

WITH new_ev AS (
	SELECT vit.id, vit.trip_id, vit.trip_segmentno, vit.segmentkey, CASE WHEN up.ev_kwh IS NULL THEN vit.ev_kwh ELSE up.ev_kwh END AS ev_kwh
	FROM mapmatched_data.viterbi_match_osm_dk_20140101 vit
	LEFT JOIN experiments.ev_kwh_update up
	on up.trip_id = vit.trip_id AND up.trip_segmentno = vit.trip_segmentno
)
UPDATE experiments.rmp10_viterbi_match_osm_dk_20140101_overlap os
SET ev_kwh = CASE WHEN os.origin = os.id THEN upd.ev_kwh ELSE upd.ev_kwh / 2 END
FROM new_ev upd
WHERE os.origin = upd.id;

UPDATE experiments.rmp10_viterbi_match_osm_dk_20140101_overlap os
SET ev_soc_trip = ev_soc_agg,
	meters_driven_trip = meters_driven_agg,
	meters_segment_trip = meters_segment_agg,
	seconds_trip = seconds_agg,
	ev_kwh_trip = ev_kwh_agg
FROM (
	SELECT 
		sum(ev_soc) OVER (
			PARTITION BY trip_id 
			ORDER BY trip_id, trip_segmentno
		) as ev_soc_agg,
		sum(meters_driven) OVER (
			PARTITION BY trip_id 
			ORDER BY trip_id, trip_segmentno
		) as meters_driven_agg,
		sum(meters_segment) OVER (
			PARTITION BY trip_id 
			ORDER BY trip_id, trip_segmentno
		) as meters_segment_agg,
		sum(seconds) OVER (
			PARTITION BY trip_id 
			ORDER BY trip_id, trip_segmentno
		) as seconds_agg,
		sum(ev_kwh) OVER (
			PARTITION BY trip_id 
			ORDER BY trip_id, trip_segmentno
		) as ev_kwh_agg,
		id
	FROM experiments.rmp10_viterbi_match_osm_dk_20140101_overlap
) ss
WHERE os.id = ss.id;

CREATE INDEX rmp10_ixd_datekey_rmp10_viterbi
    ON experiments.rmp10_viterbi_match_osm_dk_20140101_overlap USING btree
    (datekey)
    TABLESPACE pg_default;

CREATE INDEX rmp10_trip_with_segments_multi_index
    ON experiments.rmp10_viterbi_match_osm_dk_20140101_overlap USING btree
    (trip_id, trip_segmentno)
    TABLESPACE pg_default;

CREATE INDEX rmp10_viterbi_match_osm_dk_20140101_segmentkey_index
    ON experiments.rmp10_viterbi_match_osm_dk_20140101_overlap USING btree
    (segmentkey DESC NULLS LAST)
    TABLESPACE pg_default;

CREATE INDEX rmp10_viterbi_match_osm_dk_20140101_segmentkey_index_asc
    ON experiments.rmp10_viterbi_match_osm_dk_20140101_overlap USING btree
    (segmentkey ASC NULLS LAST)
    TABLESPACE pg_default;

CREATE INDEX rmp10_viterbi_match_osm_dk_20140101_trip_id_index
    ON experiments.rmp10_viterbi_match_osm_dk_20140101_overlap USING btree
    (trip_id)
    TABLESPACE pg_default;