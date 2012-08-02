# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Series'
        db.create_table('ponylib_series', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.TextField')()),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated_at', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('ponylib', ['Series'])

        # Adding model 'Genre'
        db.create_table('ponylib_genre', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('code', self.gf('django.db.models.fields.CharField')(unique=True, max_length=40)),
            ('value_ru', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('value_en', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('protect', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('ponylib', ['Genre'])

        # Adding model 'Author'
        db.create_table('ponylib_author', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('fullname', self.gf('django.db.models.fields.TextField')()),
            ('firstname', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('middlename', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('lastname', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('nickname', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('homepage', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('email', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated_at', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('ponylib', ['Author'])

        # Adding model 'Root'
        db.create_table('ponylib_root', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('path', self.gf('django.db.models.fields.TextField')()),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated_at', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('ponylib', ['Root'])

        # Adding model 'Book'
        db.create_table('ponylib_book', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.TextField')()),
            ('rel_path', self.gf('django.db.models.fields.TextField')()),
            ('isbn', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('annotation', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('publisher', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('pubyear', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('root', self.gf('django.db.models.fields.related.ForeignKey')(related_name='Books', to=orm['ponylib.Root'])),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated_at', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('ponylib', ['Book'])

        # Adding model 'BookSeries'
        db.create_table('ponylib_book_series', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('series', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ponylib.Series'])),
            ('book', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ponylib.Book'])),
            ('number', self.gf('django.db.models.fields.CharField')(max_length=20)),
        ))
        db.send_create_signal('ponylib', ['BookSeries'])

        # Adding model 'BookGenre'
        db.create_table('ponylib_book_genre', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('genre', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ponylib.Genre'])),
            ('book', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ponylib.Book'])),
        ))
        db.send_create_signal('ponylib', ['BookGenre'])

        # Adding model 'BookAuthor'
        db.create_table('ponylib_book_author', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('author', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ponylib.Author'])),
            ('book', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ponylib.Book'])),
        ))
        db.send_create_signal('ponylib', ['BookAuthor'])


    def backwards(self, orm):
        # Deleting model 'Series'
        db.delete_table('ponylib_series')

        # Deleting model 'Genre'
        db.delete_table('ponylib_genre')

        # Deleting model 'Author'
        db.delete_table('ponylib_author')

        # Deleting model 'Root'
        db.delete_table('ponylib_root')

        # Deleting model 'Book'
        db.delete_table('ponylib_book')

        # Deleting model 'BookSeries'
        db.delete_table('ponylib_book_series')

        # Deleting model 'BookGenre'
        db.delete_table('ponylib_book_genre')

        # Deleting model 'BookAuthor'
        db.delete_table('ponylib_book_author')


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
            'isbn': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'publisher': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'pubyear': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'rel_path': ('django.db.models.fields.TextField', [], {}),
            'root': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'Books'", 'to': "orm['ponylib.Root']"}),
            'series': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['ponylib.Series']", 'symmetrical': 'False', 'through': "orm['ponylib.BookSeries']", 'blank': 'True'}),
            'title': ('django.db.models.fields.TextField', [], {}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'ponylib.bookauthor': {
            'Meta': {'object_name': 'BookAuthor', 'db_table': "'ponylib_book_author'"},
            'author': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ponylib.Author']"}),
            'book': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ponylib.Book']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'ponylib.bookgenre': {
            'Meta': {'object_name': 'BookGenre', 'db_table': "'ponylib_book_genre'"},
            'book': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ponylib.Book']"}),
            'genre': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ponylib.Genre']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'ponylib.bookseries': {
            'Meta': {'object_name': 'BookSeries', 'db_table': "'ponylib_book_series'"},
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