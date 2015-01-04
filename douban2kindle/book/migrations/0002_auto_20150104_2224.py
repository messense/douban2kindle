# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('book', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='book',
            name='cover',
            field=models.CharField(max_length=500, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='book',
            name='path',
            field=models.CharField(max_length=500, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='book',
            name='subtitle',
            field=models.CharField(max_length=200, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='book',
            name='title',
            field=models.CharField(max_length=200, db_index=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='bookimage',
            name='book',
            field=models.ForeignKey(related_name='images', to='book.Book'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='bookimage',
            name='src',
            field=models.CharField(max_length=255, db_index=True),
            preserve_default=True,
        ),
    ]
