drop table if exists experiments.rmp10_all_trip_supersegments;

with superseg_trips as (
	select
		s1.trip_id,
		s1.trip_segmentno as start_segmentno,
		s2.trip_segmentno as end_segmentno,
		sups.*
	from experiments.rmp10_all_supersegments sups
	join experiments.rmp10_viterbi_match_osm_dk_20140101_overlap s1
	on sups.segments[1]=s1.segmentkey
	join experiments.rmp10_viterbi_match_osm_dk_20140101_overlap s2
	on 
		sups.segments[array_length(segments, 1)]=s2.segmentkey and
		s1.trip_id=s2.trip_id and
		s1.trip_segmentno=s2.trip_segmentno - (array_length(segments, 1) - 1)
)
select
	sst.superseg_id,
	sst.trip_id,
	sst.start_segmentno,
	sst.end_segmentno,
	trip_segments_count,
	(SELECT SUM(s) FROM UNNEST(ta.meters_segment_arr[sst.start_segmentno:sst.end_segmentno]) s) AS meters_segment,
	(SELECT SUM(s) FROM UNNEST(ta.meters_driven_arr[sst.start_segmentno:sst.end_segmentno]) s) AS meters_driven,
	(SELECT SUM(s) FROM UNNEST(ta.seconds_arr[sst.start_segmentno:sst.end_segmentno]) s) AS seconds,
	(SELECT SUM(s) FROM UNNEST(ta.ev_kwh_arr[sst.start_segmentno:sst.end_segmentno]) s) * 1000 AS ev_wh,
	(SELECT MIN(s) FROM UNNEST(ta.datekey_arr[sst.start_segmentno:sst.end_segmentno]) s) AS datekey,
	(SELECT MIN(s) FROM UNNEST(ta.timekey_arr[sst.start_segmentno:sst.end_segmentno]) s) AS timekey,
	(SELECT MIN(s) FROM UNNEST(ta.weathermeasurekey_arr[sst.start_segmentno:sst.end_segmentno]) s) AS weathermeasurekey,
	ta.id_arr[sst.start_segmentno:sst.end_segmentno] as id_arr
into experiments.rmp10_all_trip_supersegments
from superseg_trips sst
join experiments.rmp10_trips_aggregated ta
on 
	sst.trip_id=ta.trip_id and
	sst.segments=ta.segmentkeys_arr[sst.start_segmentno:sst.end_segmentno];

-- indexes (takes about 4 minutes)
CREATE INDEX rmp10_all_trip_supersegments_id_arr_btree_idx
    ON experiments.rmp10_all_trip_supersegments USING btree
    (id_arr)
    TABLESPACE pg_default;
CREATE INDEX rmp10_all_trip_supersegments_id_arr_gin_idx
    ON experiments.rmp10_all_trip_supersegments USING gin
    (id_arr)
    TABLESPACE pg_default;
CREATE INDEX rmp10_all_trip_supersegments_superseg_id_idx
    ON experiments.rmp10_all_trip_supersegments USING btree
    (superseg_id)
    TABLESPACE pg_default;
CREATE INDEX rmp10_all_trip_supersegments_trip_id_idx
    ON experiments.rmp10_all_trip_supersegments USING btree
    (trip_id)
    TABLESPACE pg_default;

