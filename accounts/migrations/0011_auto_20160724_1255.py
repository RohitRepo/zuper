# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-07-24 12:55
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0010_user_is_staff'),
    ]

    operations = [
        migrations.AlterField(
            model_name='useraddress',
            name='latitude',
            field=models.CharField(max_length=30),
        ),
        migrations.AlterField(
            model_name='useraddress',
            name='longitude',
            field=models.CharField(max_length=30),
        ),
    ]
