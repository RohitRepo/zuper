# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-04-21 11:20
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_user_user_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='user_type',
            field=models.CharField(choices=[(b'CU', b'Customer'), (b'AG', b'Agent')], default=b'CU', max_length=2),
        ),
    ]