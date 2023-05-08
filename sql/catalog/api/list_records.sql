-- list_records()
EXPLAIN
SELECT count(*) AS count_1
FROM (SELECT 1
      FROM catalog_record
      WHERE catalog_record.catalog_id = :catalog_id_1
        AND (catalog_record.searchable IS NULL OR catalog_record.searchable)
        AND catalog_record.published) AS anon_1;
EXPLAIN
SELECT 1
FROM catalog_record
WHERE catalog_record.catalog_id = :catalog_id_1
  AND (catalog_record.searchable IS NULL OR catalog_record.searchable)
  AND catalog_record.published
ORDER BY catalog_record.timestamp
LIMIT :param_1 OFFSET :param_2;

-- list_records(include_nonsearchable)
EXPLAIN
SELECT count(*) AS count_1
FROM (SELECT 1
      FROM catalog_record
      WHERE catalog_record.catalog_id = :catalog_id_1
        AND catalog_record.published) AS anon_1;
EXPLAIN
SELECT 1
FROM catalog_record
WHERE catalog_record.catalog_id = :catalog_id_1
  AND catalog_record.published
ORDER BY catalog_record.timestamp
LIMIT :param_1 OFFSET :param_2;

-- list_records(include_retracted)
EXPLAIN
SELECT count(*) AS count_1
FROM (SELECT 1
      FROM catalog_record
               JOIN published_record ON catalog_record.record_id = published_record.id
      WHERE catalog_record.catalog_id = :catalog_id_1
        AND (catalog_record.searchable IS NULL OR catalog_record.searchable)) AS anon_1;
EXPLAIN
SELECT 1
FROM catalog_record
         JOIN published_record ON catalog_record.record_id = published_record.id
WHERE catalog_record.catalog_id = :catalog_id_1
  AND (catalog_record.searchable IS NULL OR catalog_record.searchable)
ORDER BY catalog_record.timestamp
LIMIT :param_1 OFFSET :param_2;

-- list_records(include_nonsearchable, include_retracted)
EXPLAIN
SELECT count(*) AS count_1
FROM (SELECT 1
      FROM catalog_record
               JOIN published_record ON catalog_record.record_id = published_record.id
      WHERE catalog_record.catalog_id = :catalog_id_1) AS anon_1;
EXPLAIN
SELECT 1
FROM catalog_record
         JOIN published_record ON catalog_record.record_id = published_record.id
WHERE catalog_record.catalog_id = :catalog_id_1
ORDER BY catalog_record.timestamp
LIMIT :param_1 OFFSET :param_2;
