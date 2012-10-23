# _*_ coding: utf-8 _*_
from __future__ import unicode_literals

__license__ = 'GPL v3'
__copyright__ = 'Copyright 2012 maizy.ru'
__author__ = 'Nikita Kovaliov <nikita@maizy.ru>'

__version__ = '0.1'

import os.path as path
from mock import patch

import django.test
from django.conf import settings

from ponylib.models import Book, BookSeries, Genre
from ponylib.scanner.consumer import AddOrUpdateBookConsumer
from ponylib.tests import generate_rand_phrase, generate_rand_word


class AddBookConsumerTestCase(django.test.TestCase):

    sample_fb2 = None
    sample_root = None

    def setUp(self):
        self.sample_root = path.join(settings.PROJECT_ROOT, 'data', 'test-fb2')
        self.sample_fb2 = 'utf8-the-ebook.org-test.fb2'


    def tearDown(self):
        pass

    def test_over_max_length_strings(self):
        """Issue #52"""

        series_index_maxlen = BookSeries._meta.get_field_by_name('number')[0].max_length
        genre_code_maxlen = Genre._meta.get_field_by_name('code')[0].max_length
        #format in ponylib.meta.read_fb2_meta()
        mock_meta = {
            #unlimited field
            'title': generate_rand_word(1986),

            #limited fields
            'genres': [generate_rand_word(genre_code_maxlen*2)],
            'series': [{'name': generate_rand_word(1111), 'index': generate_rand_word(series_index_maxlen*2)}]
        }

        with patch.object(AddOrUpdateBookConsumer, '_read_meta_data', return_value=(mock_meta, True)):

            consumer = AddOrUpdateBookConsumer(kwargs={'connection_alias': 'default'})
            consumer.allow_update = False

            book = consumer._process_path(self.sample_root, self.sample_fb2)
            book_id = book.id
            book_from_db = Book.objects.get(pk=book_id)

            #unlimited field
            self.assertEqual(book_from_db.title, mock_meta['title'])

            #limited fiels
            self.assertEqual(book_from_db.series.count(), 1)
            self.assertEquals(
                book_from_db.get_series_links()[0].number,
                mock_meta['series'][0]['index'][:series_index_maxlen-3] + '...')

            self.assertEqual(book_from_db.genres.count(), 1)
            self.assertEquals(book_from_db.genres.all()[0].code, mock_meta['genres'][0][:genre_code_maxlen])


    #TODO: consumer_without_stat_test