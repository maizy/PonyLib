# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Book.index_a'
        db.add_column('ponylib_book', 'index_a',
                      self.gf('django.db.models.fields.TextField')(default=''),
                      keep_default=False)

        # Adding field 'Book.index_c'
        db.add_column('ponylib_book', 'index_c',
                      self.gf('django.db.models.fields.TextField')(default=''),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Book.index_a'
        db.delete_column('ponylib_book', 'index_a')

        # Deleting field 'Book.index_c'
        db.delete_column('ponylib_book', 'index_c')


    models = {
        'ponylib.author': {
            'Meta': {'object_name': 'Author'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'firstname': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'fullname': ('django.db.models.fields.TextField', [], {}),
            'homepage': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lastname': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'middlename': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'nickname': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'ponylib.book': {
            'Meta': {'object_name': 'Book'},
            'annotation': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'authors': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['ponylib.Author']", 'symmetrical': 'False', 'through': "orm['ponylib.BookAuthor']", 'blank': 'True'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'genres': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['ponylib.Genre']", 'symmetrical': 'False', 'through': "orm['ponylib.BookGenre']", 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'index_a': ('django.db.models.fields.TextField', [], {}),
            'index_c': ('django.db.models.fields.TextField', [], {}),
            'isbn': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'publisher': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'pubyear': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'rel_path': ('django.db.models.fields.TextField', [], {}),
            'root': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'Books'", 'to': "orm['ponylib.Root']"}),
            'series': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['ponylib.Series']", 'symmetrical': 'False', 'through': "orm['ponylib.BookSeries']", 'blank': 'True'}),
            'title': ('django.db.models.fields.TextField', [], {}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'ponylib.bookauthor': {
            'Meta': {'object_name': 'BookAuthor', 'db_table': "u'ponylib_book_author'"},
            'author': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ponylib.Author']"}),
            'book': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ponylib.Book']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'ponylib.bookgenre': {
            'Meta': {'object_name': 'BookGenre', 'db_table': "u'ponylib_book_genre'"},
            'book': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ponylib.Book']"}),
            'genre': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ponylib.Genre']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'ponylib.bookseries': {
            'Meta': {'object_name': 'BookSeries', 'db_table': "u'ponylib_book_series'"},
            'book': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ponylib.Book']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'number': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'series': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ponylib.Series']"})
        },
        'ponylib.genre': {
            'Meta': {'object_name': 'Genre'},
            'code': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '40'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'protect': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'value_en': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'value_ru': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'})
        },
        'ponylib.root': {
            'Meta': {'object_name': 'Root'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'path': ('django.db.models.fields.TextField', [], {}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'ponylib.series': {
            'Meta': {'object_name': 'Series'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.TextField', [], {}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['ponylib']