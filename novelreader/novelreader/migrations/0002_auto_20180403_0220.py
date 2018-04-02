# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2018-04-02 18:20
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('novelreader', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserFavorite',
            fields=[
                ('id', models.IntegerField(auto_created=True, primary_key=True, serialize=False)),
                ('novel_id', models.IntegerField()),
                ('novel_name', models.CharField(max_length=100)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AlterIndexTogether(
            name='userfavorite',
            index_together=set([('user', 'novel_id')]),
        ),
    ]
