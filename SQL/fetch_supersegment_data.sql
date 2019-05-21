DROP VIEW IF EXISTS experiments.supersegments_training_data_temp_view;
CREATE VIEW experiments.supersegments_training_data_temp_view AS
	SELECT
		*
	FROM experiments.rmp10_all_trip_data atd
	WHERE EXISTS (
		SELECT
		FROM experiments.rmp10_training t
		WHERE t.id=any(atd.id_arr)
	);

\copy (SELECT * FROM experiments.supersegments_training_data_temp_view) TO '../Models/data/supersegment-data.csv' HEADER CSV;

