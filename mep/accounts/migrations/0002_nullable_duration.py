# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-10-10 13:35
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        # also rolls up currency choice changes to subscribe class
        migrations.AlterField(
            model_name='subscribe',
            name='currency',
            field=models.CharField(blank=True, choices=[('', '----'), ('USD', 'US Dollar'), ('FRF', 'French Franc'), ('GBP', 'British Pound')], max_length=3),
        ),
        migrations.AlterField(
            model_name='subscribe',
            name='duration',
            field=models.PositiveSmallIntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='subscribe',
            name='modification',
            field=models.CharField(blank=True, choices=[('', '----'), ('sup', 'Supplement'), ('ren', 'Renewal')], max_length=50),
        ),
    ]
