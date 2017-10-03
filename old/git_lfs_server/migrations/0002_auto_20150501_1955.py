# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('git_lfs_server', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lfsaccess',
            name='user',
            field=models.CharField(max_length=32, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='lfsobject',
            name='uploader',
            field=models.CharField(max_length=32, null=True, blank=True),
        ),
    ]
