# _*_ coding: utf-8 _*_
from __future__ import unicode_literals

__license__ = 'GPL v3'
__copyright__ = 'Copyright 2012 maizy.ru'
__author__ = 'Nikita Kovaliov <nikita@maizy.ru>'

__version__ = '0.1'

import django.test

from ponylib.models import Series, Author
from ponylib.tests import generate_rand_word, generate_rand_phrase

class CacheTestCase(django.test.TestCase):

    def test_get_by_ANY_or_create(self):
        manager = Series.objects
        ph1 = generate_rand_word(4)
        obj1 = manager.get_by_name_or_create(ph1)
        obj2 = manager.get_by_name_or_create(generate_rand_word(5))
        self.assertNotEqual(obj1.id, obj2.id)
        obj1_again = manager.get_by_name_or_create(ph1)
        self.assertEqual(obj1_again.id, obj1.id)

    def test_get_id_by_ANY_or_create(self):
        manager = Author.objects
        ph1 = generate_rand_word(4)
        obj1_id = manager.get_id_by_fullname_or_create(ph1)
        obj2_id = manager.get_id_by_fullname_or_create(generate_rand_word(5))
        self.assertIsInstance(obj1_id, int)
        self.assertNotEqual(obj1_id, obj2_id)
        obj1_again_id = manager.get_id_by_fullname_or_create(ph1)
        self.assertEquals(obj1_again_id, obj1_id)
