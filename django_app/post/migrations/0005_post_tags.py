# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-06-20 05:54
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('post', '0004_remove_post_tags'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='tags',
            field=models.ManyToManyField(to='post.Tag'),
        ),
    ]
