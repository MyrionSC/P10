DROP TABLE IF EXISTS experiments.rmp10_all_trip_supersegments;

select
	s1.trip_id,
	s1.trip_segmentno as start_segmentno,
	s2.trip_segmentno as end_segmentno,
	sups.segments,
	sups.type
into experiments.rmp10_all_trip_supersegments
from experiments.rmp10_all_supersegments sups
join experiments.rmp10_viterbi_match_osm_dk_20140101_overlap s1
on sups.segments[1]=s1.segmentkey
join experiments.rmp10_viterbi_match_osm_dk_20140101_overlap s2
on 
	sups.segments[array_length(segments, 1)]=s2.segmentkey and
	s1.trip_id=s2.trip_id and
	s1.trip_segmentno=s2.trip_segmentno - array_length(segments, 1) + 1;

CREATE INDEX rmp10_all_trip_supersegments_trip_idx
    ON experiments.rmp10_all_trip_supersegments USING btree
    (trip_id ASC NULLS LAST)
    TABLESPACE pg_default;
CREATE INDEX rmp10_all_trip_supersegments_segments_idx
    ON experiments.rmp10_all_trip_supersegments USING btree
    (segments ASC NULLS LAST)
    TABLESPACE pg_default;

-- delete fake positives
DELETE
FROM experiments.rmp10_all_trip_supersegments ats
WHERE EXISTS (
	SELECT
	FROM experiments.rmp10_trips_aggregated
	WHERE
		ats.trip_id = trip_id and 
		ats.segments != segmentkeys_arr[ats.start_segmentno: ats.end_segmentno]
);

-- add new rows
ALTER TABLE experiments.rmp10_all_trip_supersegments
ADD COLUMN trip_segments_count integer,
ADD COLUMN meters_segment real,
ADD COLUMN meters_driven real,
ADD COLUMN seconds real,
ADD COLUMN ev_wh double precision,
ADD COLUMN weathermeasurekey integer,
ADD COLUMN datekey integer,
ADD COLUMN timekey smallint;

UPDATE experiments.rmp10_all_trip_supersegments AS ats
SET 
	trip_segments_count = ta.trip_segments_count, 
	meters_segment = (SELECT SUM(s) FROM UNNEST(ta.meters_segment_arr[ats.start_segmentno:ats.end_segmentno]) s),
	meters_driven = (SELECT SUM(s) FROM UNNEST(ta.meters_driven_arr[ats.start_segmentno:ats.end_segmentno]) s),
	seconds = (SELECT SUM(s) FROM UNNEST(ta.seconds_arr[ats.start_segmentno:ats.end_segmentno]) s),
	ev_wh = (SELECT SUM(s) FROM UNNEST(ta.ev_kwh_arr[ats.start_segmentno:ats.end_segmentno]) s) * 1000,
	datekey = (SELECT MIN(s) FROM UNNEST(ta.datekey_arr[ats.start_segmentno:ats.end_segmentno]) s),
	timekey = (SELECT MIN(s) FROM UNNEST(ta.timekey_arr[ats.start_segmentno:ats.end_segmentno]) s),
	weathermeasurekey = (SELECT MIN(s) FROM UNNEST(ta.weathermeasurekey_arr[ats.start_segmentno:ats.end_segmentno]) s)
FROM experiments.rmp10_trips_aggregated ta
WHERE
	ats.trip_id = ta.trip_id and
	ats.segments = ta.segmentkeys_arr[ats.start_segmentno:ats.end_segmentno];

CREATE INDEX rmp10_all_trip_supersegments_ixd_datekey_viterbi
    ON experiments.rmp10_all_trip_supersegments USING btree
    (datekey)
    TABLESPACE pg_default;

/*CREATE INDEX rmp10_all_trip_supersegments_trip_with_segments_multi_index
    ON experiments.rmp10_all_trip_supersegments USING btree
    (trip_id, trip_segmentno)
    TABLESPACE pg_default;*/

CREATE INDEX rmp10_all_trip_supersegments_supersegs_segments_index_desc
    ON experiments.rmp10_training_supersegs USING btree
    (segments DESC NULLS LAST)
    TABLESPACE pg_default;

CREATE INDEX rmp10_all_trip_supersegments_supersegs_segments_index_asc
    ON experiments.rmp10_training_supersegs USING btree
    (segments ASC NULLS LAST)
    TABLESPACE pg_default;

CREATE INDEX rmp10_training_supersegs_trip_id_index
    ON experiments.rmp10_training_supersegs USING btree
    (trip_id)
    TABLESPACE pg_default;

ALTER TABLE experiments.rmp10_all_trip_supersegments
DROP COLUMN id,
ADD COLUMN id_arr bigint[];

UPDATE experiments.rmp10_all_trip_supersegments ss
SET id_arr = sub2.id_arr
FROM (
	SELECT trip_id, start_segmentno, end_segmentno, array_agg(id) as id_arr
	FROM (
		SELECT ss.trip_id, ss.start_segmentno, ss.end_segmentno, os.trip_segmentno, os.id
		FROM experiments.rmp10_all_trip_supersegments ss
		JOIN experiments.rmp10_viterbi_match_osm_dk_20140101_overlap os
		ON ss.trip_id = os.trip_id 
		AND os.trip_segmentno >= ss.start_segmentno 
		AND os.trip_segmentno <= ss.end_segmentno
		ORDER BY os.trip_id, os.trip_segmentno
	) sub
	GROUP BY trip_id, start_segmentno, end_segmentno
	ORDER BY trip_id, start_segmentno
) sub2
WHERE ss.trip_id = sub2.trip_id
AND ss.start_segmentno = sub2.start_segmentno 
AND ss.end_segmentno = sub2.end_segmentno;

UPDATE experiments.rmp10_all_trip_supersegments tss
SET ev_wh = ss.ev_kwh * 1000
FROM (
	SELECT id_arr, sum(ev_kwh) as ev_kwh
	FROM (
		SELECT id_arr, unnest(id_arr) as id
		FROM experiments.rmp10_all_trip_supersegments
	) t1
	JOIN experiments.rmp10_viterbi_match_osm_dk_20140101_overlap t2
	ON t1.id = t2.id
	GROUP BY t1.id_arr
) ss
WHERE ss.id_arr = tss.id_arr;







