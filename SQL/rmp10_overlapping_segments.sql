CREATE TABLE experiments.rmp10_overlapping_segments AS
SELECT segment, count(segment)
FROM (
	SELECT
		CASE WHEN (ss1.startseg = ss2.startseg) 
			 OR (ss1.startseg = ss2.endseg) 
			 THEN ss1.startseg
			 ELSE ss1.endseg
		END AS segment
	FROM experiments.rmp10_all_supersegments ss1
	JOIN experiments.rmp10_all_supersegments ss2
	ON (ss1.startseg = ss2.startseg AND ss1.startpoint <> ss2.startpoint)
	OR (ss1.startseg = ss2.endseg   AND ss1.startpoint <> ss2.endpoint)
	OR (ss1.endseg 	 = ss2.startseg AND ss1.endpoint   <> ss2.startpoint)
	OR (ss1.endseg   = ss2.endseg   AND ss1.endpoint   <> ss2.endpoint)
) sub
GROUP BY segment
