CREATE TABLE maps.energy_predictions
(
	segmentkey BIGSERIAL PRIMARY KEY,
	ev_wh float
);

COPY maps.energy_predictions (segmentkey, ev_wh)
FROM '/home/rmp10/P10/Models/data/energy_predictions.csv'
CSV
DELIMITER ';'
ENCODING 'UTF8';

CREATE TABLE maps.energy_predictions
(
	segmentkey BIGSERIAL PRIMARY KEY,
	ev_wh float
);

COPY maps.energy_predictions (segmentkey, ev_wh)
FROM '/home/rmp10/P10/Models/data/energy_predictions.csv'
CSV
DELIMITER ';'
ENCODING 'UTF8';

ALTER TABLE maps.routing2
ADD COLUMN ev_wh float;

UPDATE maps.routing2
SET ev_wh = maps.energy_predictions.ev_wh
FROM maps.energy_predictions
WHERE maps.routing2.segmentkey = maps.energy_predictions.segmentkey;
