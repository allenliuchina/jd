# Generated by Django 2.1.3 on 2018-11-17 08:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('good', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='good',
            old_name='file',
            new_name='image',
        ),
        migrations.AddField(
            model_name='goodtype',
            name='image',
            field=models.ImageField(null=True, upload_to='image/category/'),
        ),
        migrations.AlterField(
            model_name='good',
            name='type',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='good', to='good.GoodType'),
        ),
    ]
