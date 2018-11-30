# Generated by Django 2.1.3 on 2018-11-17 10:03

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('good', '0004_good_desc'),
    ]

    operations = [
        migrations.CreateModel(
            name='GoodComment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('comment', models.CharField(max_length=150)),
                ('create_time', models.DateTimeField(auto_now_add=True)),
                ('good', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='good.Good')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
