# Generated by Django 2.1.3 on 2018-12-16 08:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cart', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cart',
            name='user',
        ),
        migrations.DeleteModel(
            name='Cart',
        ),
    ]
