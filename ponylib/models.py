# _*_ coding: utf-8 _*_

__license__         = "GPLv3"
__copyright__       = "Copyright 2011 maizy.ru"
__author__          = "Nikita Kovaliov <nikita@maizy.ru>"

__version__         = "0.1"
__doc__             = ""


from django.db import models
from django.core.exceptions import ObjectDoesNotExist

_prefix = 'ponylib_'

# -------------------------------------------
# Managers (table-level)

class _BaseManager(models.Manager):

    def _get_or_create(self, field, value, save=True, create_args=None):

        if create_args is None:
            create_args = {}

        args = {field: value}
        try:
            row = self.get(**args)

        except ObjectDoesNotExist:
            create_args.update(args)
            row = self.create(**create_args)
            if save:
                row.save()

        return row



class RootManager(_BaseManager):

    def get_by_path_or_create(self, path):
        return self._get_or_create('path', path)


class AuthorManager(_BaseManager):

    def get_by_fullname_or_create(self, fullname):
        return self._get_or_create('fullname', fullname)

class GenreManager(_BaseManager):

    def get_by_name_or_create(self, name):
        return self._get_or_create('name', name)

class SeriesManager(_BaseManager):

    def get_by_name_or_create(self, name):
        return self._get_or_create('name', name)

# -------------------------------------------
# Objects (row-level)

class Series(models.Model):

    name = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = SeriesManager()


class Genre(models.Model):

    code = models.CharField(max_length=40)
    value = models.CharField(max_length=255, blank=True)
    protect = models.BooleanField(default=False)

    objects = GenreManager()


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


class Root(models.Model):

    path = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = RootManager()


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


# -------------------------------------------
# M-M
class BookSeries(models.Model):

    series = models.ForeignKey('Series')
    book = models.ForeignKey('Book')

    number = models.CharField(max_length=20)

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
