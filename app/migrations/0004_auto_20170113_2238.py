# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2017-01-14 03:38
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0003_auto_20170113_2234'),
    ]

    operations = [
        migrations.RenameField(
            model_name='line',
            old_name='categories',
            new_name='category',
        ),
        migrations.RenameField(
            model_name='line',
            old_name='tags',
            new_name='tag',
        ),
    ]
