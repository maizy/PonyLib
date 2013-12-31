-- Strip duplicates
-- Posgres only

-- SELECT a.id
-- FROM ponylib_book as a 
-- WHERE a.id IN (
--     SELECT id
--     FROM (
--         SELECT b.id, row_number() over (partition BY b.root_id, b.rel_path ORDER BY b.id) AS rnum
--         FROM ponylib_book as b
--     ) AS t
--     WHERE t.rnum > 1
-- );

DELETE FROM ponylib_book_author as l 
WHERE l.book_id IN (
    SELECT a.id
    FROM ponylib_book as a 
    WHERE a.id IN (
        SELECT id
        FROM (
            SELECT b.id, row_number() over (partition BY b.root_id, b.rel_path ORDER BY b.id) AS rnum
            FROM ponylib_book as b
        ) AS t
        WHERE t.rnum > 1
    )
);

DELETE FROM ponylib_book_genre as l 
WHERE l.book_id IN (
    SELECT a.id
    FROM ponylib_book as a 
    WHERE a.id IN (
        SELECT id
        FROM (
            SELECT b.id, row_number() over (partition BY b.root_id, b.rel_path ORDER BY b.id) AS rnum
            FROM ponylib_book as b
        ) AS t
        WHERE t.rnum > 1
    )
);

DELETE FROM ponylib_book_series as l 
WHERE l.book_id IN (
    SELECT a.id
    FROM ponylib_book as a 
    WHERE a.id IN (
        SELECT id
        FROM (
            SELECT b.id, row_number() over (partition BY b.root_id, b.rel_path ORDER BY b.id) AS rnum
            FROM ponylib_book as b
        ) AS t
        WHERE t.rnum > 1
    )
);

DELETE FROM ponylib_book as a 
WHERE a.id IN (
    SELECT id
    FROM (
        SELECT b.id, row_number() over (partition BY b.root_id, b.rel_path ORDER BY b.id) AS rnum
        FROM ponylib_book as b
    ) AS t
    WHERE t.rnum > 1
);