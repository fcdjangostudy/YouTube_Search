# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-06-26 06:04
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('member', '0010_auto_20170626_0603'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='user_type',
            field=models.CharField(choices=[('d', 'django'), ('f', 'facebook')], default='d', max_length=1),
        ),
    ]
