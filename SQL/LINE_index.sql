CREATE UNIQUE INDEX embeddings_line_segmentkey_idx
    ON embeddings.line USING btree
    (segmentkey)
    TABLESPACE pg_default;