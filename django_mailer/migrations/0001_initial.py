# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Message'
        db.create_table('django_mailer_message', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('to_address', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('from_address', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('subject', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('encoded_message', self.gf('django.db.models.fields.TextField')()),
            ('date_created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
        ))
        db.send_create_signal('django_mailer', ['Message'])

        # Adding model 'QueuedMessage'
        db.create_table('django_mailer_queuedmessage', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('message', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['django_mailer.Message'], unique=True)),
            ('priority', self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=3)),
            ('deferred', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('retries', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('date_queued', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
        ))
        db.send_create_signal('django_mailer', ['QueuedMessage'])

        # Adding model 'Blacklist'
        db.create_table('django_mailer_blacklist', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=200)),
            ('date_added', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
        ))
        db.send_create_signal('django_mailer', ['Blacklist'])

        # Adding model 'Log'
        db.create_table('django_mailer_log', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('message', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['django_mailer.Message'])),
            ('result', self.gf('django.db.models.fields.PositiveSmallIntegerField')()),
            ('date', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('log_message', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('django_mailer', ['Log'])


    def backwards(self, orm):
        
        # Deleting model 'Message'
        db.delete_table('django_mailer_message')

        # Deleting model 'QueuedMessage'
        db.delete_table('django_mailer_queuedmessage')

        # Deleting model 'Blacklist'
        db.delete_table('django_mailer_blacklist')

        # Deleting model 'Log'
        db.delete_table('django_mailer_log')


    models = {
        'django_mailer.blacklist': {
            'Meta': {'ordering': "('-date_added',)", 'object_name': 'Blacklist'},
            'date_added': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '200'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'django_mailer.log': {
            'Meta': {'ordering': "('-date',)", 'object_name': 'Log'},
            'date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'log_message': ('django.db.models.fields.TextField', [], {}),
            'message': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['django_mailer.Message']"}),
            'result': ('django.db.models.fields.PositiveSmallIntegerField', [], {})
        },
        'django_mailer.message': {
            'Meta': {'ordering': "('date_created',)", 'object_name': 'Message'},
            'date_created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'encoded_message': ('django.db.models.fields.TextField', [], {}),
            'from_address': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'subject': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'to_address': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'django_mailer.queuedmessage': {
            'Meta': {'ordering': "('priority', 'date_queued')", 'object_name': 'QueuedMessage'},
            'date_queued': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'deferred': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['django_mailer.Message']", 'unique': 'True'}),
            'priority': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '3'}),
            'retries': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'})
        }
    }

    complete_apps = ['django_mailer']
