Drop table if exists experiments.rmp10_all_supersegments;

select *
into experiments.rmp10_all_supersegments
from (
	select 
		segments,
		segments[1] as startseg,
		segments[array_length(segments, 1)] as endseg,
		startpoint,
		endpoint,
		array[point] as points,
		num_traversals,
		direction,
		categories,
		null as lights,
		null as traffic_lights,
		'Cat' as type
	from experiments.rmp10_category_change_supersegs
	UNION
	select 
		segments,
		segments[1] as startseg,
		segments[array_length(segments, 1)] as endseg,
		startpoint,
		endpoint,
		array[point] as points,
		num_traversals,
		direction,
		null as categories,
		lights,
		traffic_lights,
		'T' as type
	from experiments.rmp10_intersection_supersegments_t_junction_w_roundabout
	UNION
	select 
		segments,
		segments[1] as startseg,
		segments[array_length(segments, 1)] as endseg,
		startpoint,
		endpoint,
		array[point] as points,
		num_traversals,
		direction,
		null as categories,
		lights,
		traffic_lights,
		'Simple' as type
	from experiments.rmp10_intersection_supersegments_simple
	UNION 
	select
		segments,
		segments[1] as startseg,
		segments[array_length(segments, 1)] as endseg,
		startpoint,
		endpoint,
		array_remove(array_remove(rmp10_get_points(segments), startpoint), endpoint) as points,
		num_traversals,
		direction,
		null as categories,
		lights,
		traffic_lights,
		'Complex' as type
	from experiments.rmp10_intersection_supersegments_complex
) sq;

CREATE INDEX rmp10_all_supersegments_segments_array_idx1
ON experiments.rmp10_all_supersegments
USING GIN(segments);

-- remove cat changes that is subset of others. WARNING: This took 9 seconds last we ran it
DELETE
from experiments.rmp10_all_supersegments s1
where s1.type='Cat'
and exists (
	select 
	from experiments.rmp10_all_supersegments
	where s1.segments <@ segments AND type!='Cat'
);

-- add categories to everything
UPDATE experiments.rmp10_all_supersegments AS sups
SET categories=ssq.categories
FROM (
	SELECT sq.segments, sq.type, array_agg(m.category) as categories
	FROM (
		SELECT unnest(segments) as segmentkey, segments, type
		FROM experiments.rmp10_all_supersegments
		WHERE categories is null
	) sq
	JOIN maps.osm_dk_20140101 m
	ON sq.segmentkey=m.segmentkey
	GROUP BY sq.segments, sq.type
) ssq
WHERE ssq.segments=sups.segments AND ssq.type=sups.type;

-- add cat speed difference
ALTER TABLE experiments.rmp10_all_supersegments
ADD COLUMN cat_speed_difference double precision;

UPDATE experiments.rmp10_all_supersegments as s
SET cat_speed_difference=sq.cat_speed_difference
FROM (
	select 
		segments, 
		type, 
		categories, 
		categories[1] as firstcat, 
		s1.speed_avg,
		categories[array_length(categories, 1)] as lastcat,
		s2.speed_avg,
		s2.speed_avg - s1.speed_avg as cat_speed_difference
	from experiments.rmp10_all_supersegments sups
	JOIN experiments.rmp10_category_avg_speed s1
	ON sups.categories[1]=s1.category
	JOIN experiments.rmp10_category_avg_speed s2
	ON sups.categories[array_length(categories, 1)]=s2.category
) sq
WHERE s.segments=sq.segments AND s.type=sq.type;

-- add lights to type Category
UPDATE experiments.rmp10_all_supersegments s
SET lights=array[l.point], traffic_lights=true
from experiments.rmp10_trafic_light_nodes_within_30m l
where l.point=s.points[1] and s.type='Cat';

-- indexes
CREATE INDEX rmp10_all_supersegments_segments_idx1
    ON experiments.rmp10_all_supersegments USING btree
    (segments)
    TABLESPACE pg_default;
	
CREATE INDEX rmp10_all_supersegments_startpoint_idx1
    ON experiments.rmp10_all_supersegments USING btree
    (startpoint)
    TABLESPACE pg_default;
	
CREATE INDEX rmp10_all_supersegments_endpoint_idx1
    ON experiments.rmp10_all_supersegments USING btree
    (endpoint)
    TABLESPACE pg_default;
	
CREATE INDEX rmp10_all_supersegments_startseg_idx1
    ON experiments.rmp10_all_supersegments USING btree
    (startseg)
    TABLESPACE pg_default;
	
CREATE INDEX rmp10_all_supersegments_endseg_idx1
    ON experiments.rmp10_all_supersegments USING btree
    (endseg)
    TABLESPACE pg_default;

ALTER TABLE experiments.rmp10_all_supersegments
ADD COLUMN superseg_id BIGSERIAL;

CREATE TABLE experiments.rmp10_all_supersegments_original
AS TABLE experiments.rmp10_all_supersegments;

-- indexes
CREATE INDEX rmp10_all_supersegments_original_segments_idx1
    ON experiments.rmp10_all_supersegments_original USING btree
    (segments)
    TABLESPACE pg_default;
	
CREATE INDEX rmp10_all_supersegments_original_startpoint_idx1
    ON experiments.rmp10_all_supersegments_original USING btree
    (startpoint)
    TABLESPACE pg_default;
	
CREATE INDEX rmp10_all_supersegments_original_endpoint_idx1
    ON experiments.rmp10_all_supersegments_original USING btree
    (endpoint)
    TABLESPACE pg_default;
	
CREATE INDEX rmp10_all_supersegments_original_startseg_idx1
    ON experiments.rmp10_all_supersegments_original USING btree
    (startseg)
    TABLESPACE pg_default;
	
CREATE INDEX rmp10_all_supersegments_original_endseg_idx1
    ON experiments.rmp10_all_supersegments_original USING btree
    (endseg)
    TABLESPACE pg_default;

CREATE INDEX rmp10_all_supersegments_segments_original_array_idx1
	ON experiments.rmp10_all_supersegments_original USING GIN
	(segments)
	TABLESPACE pg_default;

ALTER TABLE experiments.rmp10_all_supersegments
ADD COLUMN origin bigint,
ADD COLUMN startdir text,
ADD COLUMN endir text;

UPDATE experiments.rmp10_all_supersegments
SET origin = superseg_id,
    startdir = CASE WHEN rmp10_startpoint(startseg) = startpoint THEN 'SAME' ELSE 'OTHER' END,
    endir    = CASE WHEN rmp10_endpoint  (endseg  ) = endpoint   THEN 'SAME' ELSE 'OTHER' END;

UPDATE experiments.rmp10_all_supersegments os
SET
        segments = sub.newsegs,
        startpoint = sub.startpoint,
        endpoint = sub.endpoint,
        startseg = sub.startseg,
        endseg = sub.endseg,
		superseg_id = nextval(pg_get_serial_sequence('experiments.rmp10_all_supersegments', 'superseg_id'))
FROM (
        WITH ss as (
                SELECT * FROM experiments.rmp10_all_supersegments
        ), alls as (
                SELECT 
                	ss.segments, 
                	ss.startpoint as ss_sp, 
                	ss.endpoint as ss_ep, 
                	ss.startseg, 
                	ss.endseg, 
                	ss.startdir,
                    os.segmentkey, 
                    os.startpoint as os_sp, 
                    os.endpoint as os_ep, 
                    os.origin
                FROM ss
                JOIN experiments.rmp10_osm_dk_20140101_overlaps os
                ON ss.startseg = os.origin
                AND CASE WHEN ss.startdir = 'SAME' 
                		 THEN ss.startpoint != os.startpoint
                         ELSE ss.startpoint != os.endpoint END
				AND os.origin != os.segmentkey
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
        endseg = sub.endseg,
		superseg_id = nextval(pg_get_serial_sequence('experiments.rmp10_all_supersegments', 'superseg_id'))
FROM (
        WITH ss as (
                SELECT * FROM experiments.rmp10_all_supersegments
        ), alls as (
                SELECT 
                	ss.segments, 
                	ss.startpoint as ss_sp, 
                	ss.endpoint as ss_ep, 
                	ss.startseg, 
                	ss.endseg, 
                	ss.endir,
                    os.segmentkey, 
                    os.startpoint as os_sp, 
                    os.endpoint as os_ep, 
                    os.origin
                FROM ss
                JOIN experiments.rmp10_osm_dk_20140101_overlaps os
                ON ss.endseg = os.origin
                AND CASE WHEN ss.endir = 'SAME' 
                		 THEN ss.endpoint != os.endpoint
                         ELSE ss.endpoint != os.startpoint END
				AND os.origin != os.segmentkey
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

/*ALTER TABLE experiments.rmp10_all_supersegments
DROP COLUMN startdir,
DROP COLUMN endir;*/

ALTER TABLE experiments.rmp10_all_supersegments
ADD COLUMN meters double precision;

UPDATE experiments.rmp10_all_supersegments alls
SET meters = ss.meters
FROM (
	SELECT superseg_id, sum(meters) as meters
	FROM experiments.rmp10_osm_dk_20140101_overlaps os
	JOIN (
		SELECT superseg_id, unnest(segments) as segmentkey
		FROM experiments.rmp10_all_supersegments
	) sub
	ON sub.segmentkey = os.segmentkey
	GROUP BY superseg_id
) ss
WHERE ss.superseg_id = alls.superseg_id;
