# Generated by Django 3.0.7 on 2020-08-29 22:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('show_news', '0005_auto_20200829_2201'),
    ]

    operations = [
        migrations.AlterField(
            model_name='articles',
            name='title',
            field=models.CharField(max_length=250, unique=True),
        ),
        migrations.AlterUniqueTogether(
            name='articles',
            unique_together=set(),
        ),
    ]