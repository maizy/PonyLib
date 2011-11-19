# _*_ coding: utf-8 _*_

__license__         = "GPLv3"
__copyright__       = "Copyright 2011 maizy.ru"
__author__          = "Nikita Kovaliov <nikita@maizy.ru>"

__version__         = "0.1"
__doc__             = ""


from django.db import models


_prefix = 'ponylib_'

# -------------------------------------------
# Objects

class Series(models.Model):

    name = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = _prefix+'series'


class Genre(models.Model):

    code = models.CharField(max_length=40)
    value = models.CharField(max_length=255, blank=True)
    protect = models.BooleanField(default=False)

    class Meta:
        db_table = _prefix+'genree'


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

    class Meta:
        db_table = _prefix+'author'


class Root(models.Model):

    path = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Book(models.Model):

    title = models.TextField()
    rel_path = models.TextField()

    isbn = models.TextField(blank=True)
    annotation = models.TextField(blank=True)
    publisher = models.TextField(blank=True)
    pubyear = models.IntegerField(blank=True)

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
