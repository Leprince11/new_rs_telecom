# Generated by Django 5.0.1 on 2024-03-18 13:37

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portail_web', '0003_alter_postuler_non_spontaner_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='postuler',
            name='id',
            field=models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False),
        ),
    ]