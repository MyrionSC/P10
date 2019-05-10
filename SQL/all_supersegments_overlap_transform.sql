ALTER TABLE experiments.rmp10_all_supersegments
ADD COLUMN IF NOT EXISTS segments_old integer[],
ADD COLUMN IF NOT EXISTS startpoint_old integer,
ADD COLUMN IF NOT EXISTS endpoint_old integer,
ADD COLUMN IF NOT EXISTS startdir text,
ADD COLUMN IT NOT EXISTS endir text;

UPDATE experiments.rmp10_all_supersegments
SET segments_old = segments,
	startpoint_old = startpoint,
	endpoint_old = endpoint,
    startdir = CASE WHEN rmp10_startpoint(startseg) = startpoint THEN 'SAME' ELSE 'OTHER' END,
    endir    = CASE WHEN rmp10_endpoint  (endseg  ) = endpoint   THEN 'SAME' ELSE 'OTHER' END;

UPDATE experiments.rmp10_all_supersegments os
SET
        segments = sub.newsegs,
        startpoint = sub.startpoint,
        endpoint = sub.endpoint,
        startseg = sub.startseg,
        endseg = sub.endseg
FROM (
        WITH ss as (
                SELECT * FROM experiments.rmp10_all_supersegments
        ), alls as (
                SELECT ss.segments, ss.startpoint as ss_sp, ss.endpoint as ss_ep, ss.startseg, ss.endseg, ss.startdir,
                           os.segmentkey, os.startpoint as os_sp, os.endpoint as os_ep, os.origin
                FROM ss
                JOIN experiments.rmp10_osm_dk_20140101_overlaps os
                ON ss.endseg = os.origin
                AND CASE WHEN ss.startdir = 'SAME' THEN ss.startpoint != os.startpoint
                                 ELSE ss.startpoint != os.endpoint END
                ORDER BY origin, os.startpoint
        )
        SELECT
                segments as oldsegs,
                segmentkey || segments[2:array_length(segments, 1)] as newsegs,
                CASE WHEN startdir = 'SAME' THEN os_sp ELSE os_ep END as startpoint,
                ss_ep as endpoint,
                segmentkey as startseg,
                endseg
        FROM alls
) sub
WHERE os.segments = sub.oldsegs;

UPDATE experiments.rmp10_all_supersegments os
SET
        segments = sub.newsegs,
        startpoint = sub.startpoint,
        endpoint = sub.endpoint,
        startseg = sub.startseg,
        endseg = sub.endseg
FROM (
        WITH ss as (
                SELECT * FROM experiments.rmp10_all_supersegments
        ), alls as (
                SELECT ss.segments, ss.startpoint as ss_sp, ss.endpoint as ss_ep, ss.startseg, ss.endseg, ss.endir,
                           os.segmentkey, os.startpoint as os_sp, os.endpoint as os_ep, os.origin
                FROM ss
                JOIN experiments.rmp10_osm_dk_20140101_overlaps os
                ON ss.endseg = os.origin
                AND CASE WHEN ss.endir = 'SAME' THEN ss.endpoint != os.endpoint
                                 ELSE ss.endpoint != os.startpoint END
                ORDER BY origin, os.endpoint
        )
        SELECT
                segments as oldsegs,
                segments[1:array_length(segments, 1) - 1] || segmentkey as newsegs,
                CASE WHEN endir = 'SAME' THEN os_ep ELSE os_sp END as endpoint,
                ss_sp as startpoint,
                startseg,
                segmentkey as endseg
        FROM alls
) sub
WHERE os.segments = sub.oldsegs;

ALTER TABLE experiments.rmp10_all_supersegments
DROP COLUMN startdir,
DROP COLUMN endir;