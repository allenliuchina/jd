# Generated by Django 2.1.3 on 2018-11-17 09:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('good', '0003_auto_20181117_0856'),
    ]

    operations = [
        migrations.AddField(
            model_name='good',
            name='desc',
            field=models.TextField(null=True),
        ),
    ]
