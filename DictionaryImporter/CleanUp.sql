--Re-enable FK
PRAGMA foreign_keys = true;
--Recreate Indexes
CREATE INDEX IF NOT EXISTS API_inflectionform_fk_inflection_id ON API_inflectionform (
	fk_inflection_id
);
CREATE INDEX IF NOT EXISTS API_inflection_fk_lemma_id ON API_inflection (
	fk_lemma_id
);
CREATE INDEX IF NOT EXISTS API_definition_fk_word_id ON API_definition (
	fk_word_id
);
CREATE INDEX IF NOT EXISTS API_attribute_fk_lemma_id ON API_attribute (
	fk_lemma_id
);