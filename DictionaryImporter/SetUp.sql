PRAGMA foreign_keys = false;

DROP INDEX IF EXISTS API_inflectionform_fk_inflection_id_3e55c549;
DROP INDEX IF EXISTS API_inflection_fk_lemma_id_13597281;
DROP INDEX IF EXISTS API_definition_fk_word_id_8f854651;
DROP INDEX IF EXISTS API_attribute_fk_lemma_id_1e43bda9;

DROP INDEX IF EXISTS API_inflectionform_fk_inflection_id;
DROP INDEX IF EXISTS API_inflection_fk_lemma_id;
DROP INDEX IF EXISTS API_definition_fk_word_id;
DROP INDEX IF EXISTS API_attribute_fk_lemma_id;

DELETE FROM API_attribute;
DELETE FROM API_definition;
DELETE FROM API_inflectionform;
DELETE FROM API_inflection;
DELETE FROM API_lemma;
DELETE FROM API_word;