# Generated by Django 2.1.3 on 2018-12-16 08:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('good', '0010_auto_20181205_1147'),
    ]

    operations = [
        migrations.AlterField(
            model_name='good',
            name='image',
            field=models.ImageField(null=True, upload_to='image/'),
        ),
    ]