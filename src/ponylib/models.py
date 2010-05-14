from django.db import models


_prefix = 'ponylib_'

class Sequence(models.Model):


    name = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)




class BookSequence(models.Model):

    sequence = models.ForeignKey('Sequence')
    book = models.ForeignKey('Book')

    number = models.CharField(max_length=20)

    class Meta:
        db_table = _prefix+'book_sequence'




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




class Dir(models.Model):


    path = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)




class Book(models.Model):


    title = models.TextField()
    rel_path = models.TextField()

    dir = models.ForeignKey('Dir', related_name='Books')
    authors = models.ForeignKey('Author', related_name='Books', blank=True)
    sequences = models.ManyToManyField('Sequence', through='BookSequence',\
                                       blank=True)


    created_at = models.DateTimeField(auto_now_add=True)
    modifided_at = models.DateTimeField(auto_now=True)





class ScanErrorLog(models.Model):


    fullpath = models.TextField()
    error_type = models.CharField(max_length=50, default='unknown')
    message = models.TextField(blank=True)
    exception_class = models.TextField(blank=True)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = _prefix+'scan_error_log'
