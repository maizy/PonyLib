SELECT
b.root_id,
(SELECT r.path from ponylib_root as r where r.id=b.root_id) as path,
count(1) as amount
FROM `ponylib_book` as b GROUP BY root_id