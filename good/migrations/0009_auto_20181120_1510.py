# Generated by Django 2.1.3 on 2018-11-20 07:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('good', '0008_good_stack'),
    ]

    operations = [
        migrations.RenameField(
            model_name='good',
            old_name='stack',
            new_name='stock',
        ),
    ]
