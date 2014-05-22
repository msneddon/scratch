DROP TABLE IF EXISTS pmc_articles CASCADE;
CREATE TABLE pmc_articles(
  pmid bigint UNIQUE,
  pmcid bigint UNIQUE,
  text text
);

DROP TABLE IF EXISTS pmc_sentences CASCADE;
CREATE TABLE pmc_sentences(
  document_id bigint,
  sentence text, 
  words text[],
  lemma text[],
  pos_tags text[],
  dependencies text[],
  ner_tags text[],
  sentence_id bigint -- unique identifier for sentences
  );

DROP TABLE IF EXISTS pmc_terms CASCADE;
CREATE TABLE pmc_terms(
  sentence_id bigint,
  start_position int,
  length int,
  text text,
  term_id bigint  -- unique identifier for people_mentions
  );
CREATE INDEX pmc_term_idx ON pmc_terms (text);

DROP TABLE IF EXISTS is_cellular_component CASCADE;
CREATE TABLE is_cellular_component(
  term text,
  is_true boolean,
  relation_id bigint, -- unique identifier for this cellular component
  id bigint  -- unique identifier for people_mentions
  );
CREATE INDEX is_cc_term_idx ON is_cellular_component (term);

DROP TABLE IF EXISTS is_cellular_component CASCADE;
CREATE TABLE is_cellular_component(
  term text,
  is_true boolean,
  relation_id bigint, -- unique identifier for this cellular component
  id bigint  -- unique identifier for people_mentions
  );
CREATE INDEX is_cc_term_idx ON is_cellular_component (term);
