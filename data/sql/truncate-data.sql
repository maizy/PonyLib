-- Truncate all data
--
-- do NOT run on production
-- mysql specific query, may not work in posgree
--
SET FOREIGN_KEY_CHECKS=0;

TRUNCATE `ponylib_author`;
TRUNCATE `ponylib_book`;
TRUNCATE `ponylib_book_author`;
TRUNCATE `ponylib_book_genre`;
TRUNCATE `ponylib_book_series`;
TRUNCATE `ponylib_root`;
TRUNCATE `ponylib_series`;

DELETE FROM `ponylib_genre` WHERE `protect` = 0;

SET FOREIGN_KEY_CHECKS=1;
