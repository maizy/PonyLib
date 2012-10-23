# _*_ coding: utf-8 _*_
from __future__ import unicode_literals
__license__         = "GPLv3"
__copyright__       = "Copyright 2011 maizy.ru"
__author__          = "Nikita Kovaliov <nikita@maizy.ru>"

__version__         = "0.1"
__doc__             = ""

import os
import os.path as path
import threading

from django.db import models
from django.core.exceptions import ObjectDoesNotExist
from repoze.lru import LRUCache

from ponylib.search.signals import book_index_updated

_prefix = 'ponylib_'

def get_id(func, cache_size=None):
    """
    wrapper for _BaseManager._get_or_create

    with optional lru cache
    (cache key based on first func param!)
    """

    def idzable(*args, **kwargs):
        res = func(*args, **kwargs)
        return res.id

    if cache_size is None:
        return idzable
    else:
        cache = LRUCache(size=cache_size) #global per class

        def cachable(*args, **kwargs):
            key = args[1]
            cached = cache.get(key)
            if cached:
                return cached
            else:
                val = idzable(*args, **kwargs)
                cache.put(key, val)
                return val

        return cachable


# -------------------------------------------
# Managers (table-level)

class _BaseManager(models.Manager):

    _get_or_create_lock = None
    lru_cache = None

    def __init__(self):
        super(_BaseManager, self).__init__()
        self._get_or_create_lock = threading.RLock()


    def _get_or_create(self, field, value, save=True, create_args=None, using=None):

        if create_args is None:
            create_args = {}

        qs = self.get_query_set()
        if using is not None:
            qs = qs.using(using)

        args = {field: value}
        with self._get_or_create_lock:
            try:
                row = qs.get(**args)

            except ObjectDoesNotExist:
                create_args.update(args)
                row = qs.create(**args)
                if save:
                    row.save(using=using)

        return row

class RootManager(_BaseManager):

    def get_by_path_or_create(self, path, using=None):
        return self._get_or_create('path', path, using=using)

    get_id_by_path_or_create = get_id(get_by_path_or_create, cache_size=20)


class AuthorManager(_BaseManager):

    def get_by_fullname_or_create(self, fullname, using=None):
        return self._get_or_create('fullname', fullname, using=using)

    get_id_by_fullname_or_create = get_id(get_by_fullname_or_create, cache_size=200)

class GenreManager(_BaseManager):

    def get_by_code_or_create(self, code, using=None):
        return self._get_or_create('code', code, using=using, create_args={
            'value_en' : 'Unknown (%s)' % code,
            'value_ru' : 'Неизвестно (%s)' % code,
        })

    get_id_by_code_or_create = get_id(get_by_code_or_create, cache_size=100)

class SeriesManager(_BaseManager):

    def get_by_name_or_create(self, name, using=None):
        return self._get_or_create('name', name, using=using)

    get_id_by_name_or_create = get_id(get_by_name_or_create, cache_size=100)

# -------------------------------------------
# Objects (row-level)

class Series(models.Model):

    name = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = SeriesManager()

    def __unicode__(self):
        return self.name


class Genre(models.Model):

    code = models.CharField(max_length=40, unique=True)
    value_ru = models.CharField(max_length=255, blank=True)
    value_en = models.CharField(max_length=255, blank=True)
    protect = models.BooleanField(default=False)

    objects = GenreManager()

    def __unicode__(self):
        return self.code


class Author(models.Model):

    fullname = models.TextField()

    firstname = models.CharField(max_length=255, blank=True)
    middlename = models.CharField(max_length=255, blank=True)
    lastname = models.CharField(max_length=255, blank=True)

    nickname = models.CharField(max_length=255, blank=True)
    homepage = models.TextField(blank=True)
    email = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    objects = AuthorManager()

    def __unicode__(self):
        return self.fullname


class Root(models.Model):

    path = models.TextField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = RootManager()

    def __unicode__(self):
        return self.path


class Book(models.Model):

    title = models.TextField()
    rel_path = models.TextField()

    isbn = models.TextField(blank=True)
    annotation = models.TextField(blank=True)
    publisher = models.TextField(blank=True)
    pubyear = models.IntegerField(null=True)

    root = models.ForeignKey('Root', related_name='Books')
    authors = models.ManyToManyField('Author', through='BookAuthor', blank=True)
    series = models.ManyToManyField('Series', through='BookSeries', blank=True)
    genres = models.ManyToManyField('Genre', through='BookGenre', blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    index_a = models.TextField()
    index_c = models.TextField()

    has_index_errors = models.BooleanField(default=False)

    def get_basename(self):
        return path.basename(self.rel_path)

    basename = property(get_basename)

    @property
    def full_path(self):
        return path.join(self.root.path, self.rel_path)

    def is_file_exists(self):
        return os.path.isfile(self.full_path)

    def get_series_links(self):
        return BookSeries.objects.filter(book=self)

    def __unicode__(self):
        return "id=%d, title='%s', file='%s'" % (self.id, self.title, self.get_basename())

    def update_search_index(self, save=True, using=None):

        a = []
        c = []

        a.append(self.title)

        for author in self.authors.all():
            a.append(author.fullname)

        for genre in self.genres.all():
            a.append(genre.value_ru)
            a.append(genre.value_en)

        for ser in self.series.all():
            a.append(ser.name)

        c.append(self.annotation)

        self.index_a = ' '.join(a)
        self.index_c = ' '.join(c)

        if save:
            self.save(using=using)
            book_index_updated.send(None, book=self, using=using)

    update_search_index.alters_data = True


# -------------------------------------------
# M-M
class BookSeries(models.Model):

    series = models.ForeignKey('Series')
    book = models.ForeignKey('Book')

    number = models.CharField(max_length=40)

    class Meta:
        db_table = _prefix+'book_series'

class BookGenre(models.Model):
    genre = models.ForeignKey('Genre')
    book = models.ForeignKey('Book')

    class Meta:
        db_table = _prefix+'book_genre'


class BookAuthor(models.Model):
    author = models.ForeignKey('Author')
    book = models.ForeignKey('Book')

    class Meta:
        db_table = _prefix+'book_author'


# -------------------------------------------
# system
#class ScanErrorLog(models.Model):
#
#    fullpath = models.TextField()
#    error_type = models.CharField(max_length=50, default='unknown')
#    message = models.TextField(blank=True)
#    exception_class = models.TextField(blank=True)
#    date = models.DateTimeField(auto_now_add=True)
#
#    class Meta:
#        db_table = _prefix+'scan_error_log'
