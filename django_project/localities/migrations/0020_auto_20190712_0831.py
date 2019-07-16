# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('localities', '0019_locality_migrated'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dataloader',
            name='organisation_name',
            field=models.CharField(help_text=b"Organisation's Name", max_length=100, verbose_name=b"Organisation's Name"),
        ),
    ]
