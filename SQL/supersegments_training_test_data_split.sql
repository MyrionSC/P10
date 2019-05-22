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

