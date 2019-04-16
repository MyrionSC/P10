SELECT seg, given, ev.avg_ev as single_ev, ev_given.avg_ev as given_ev
INTO experiments.rmp10_supersegments_2len_lt10_driven_ev_given
FROM ev((
    SELECT array_agg(segments[2])
    FROM experiments.rmp10_driven_supersegments_2len
    WHERE num_traversals < 10
)) JOIN ev_given ((
    SELECT array_agg(ARRAY[segments[2], segments[1]])
    FROM experiments.rmp10_driven_supersegments_2len
    WHERE num_traversals < 10
)) ON ev.segmentkey = ev_given.seg
