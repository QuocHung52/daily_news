# Generated by Django 3.0.7 on 2020-08-27 05:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('show_news', '0003_auto_20200826_2224'),
    ]

    operations = [
        migrations.AlterField(
            model_name='source_of_news',
            name='page_name',
            field=models.CharField(max_length=100, unique=True),
        ),
    ]
