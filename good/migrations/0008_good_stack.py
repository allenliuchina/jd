# Generated by Django 2.1.3 on 2018-11-20 07:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('good', '0007_good_sales'),
    ]

    operations = [
        migrations.AddField(
            model_name='good',
            name='stack',
            field=models.IntegerField(default=0),
        ),
    ]
