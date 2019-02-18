CREATE TABLE embeddings.line (
	segmentkey bigint,
	emb_0 float,
	emb_1 float,
	emb_2 float,
	emb_3 float,
	emb_4 float,
	emb_5 float,
	emb_6 float,
	emb_7 float,
	emb_8 float,
	emb_9 float,
	emb_10 float,
	emb_11 float,
	emb_12 float,
	emb_13 float,
	emb_14 float,
	emb_15 float,
	emb_16 float,
	emb_17 float,
	emb_18 float,
	emb_19 float
);

CREATE UNIQUE INDEX embeddings_line_segmentkey_idx
    ON embeddings.line USING btree
    (segmentkey)
    TABLESPACE pg_default;