DROP TABLE IF EXISTS experiments.rmp10_all_trip_supersegments;

select
	s1.trip_id,
	s1.trip_segmentno as start_segmentno,
	s2.trip_segmentno as end_segmentno,
	sups.segments,
	sups.type
into experiments.rmp10_all_trip_supersegments
from experiments.rmp10_all_supersegments sups
join mapmatched_data.viterbi_match_osm_dk_20140101 s1
on sups.segments[1]=s1.segmentkey
join mapmatched_data.viterbi_match_osm_dk_20140101 s2
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


