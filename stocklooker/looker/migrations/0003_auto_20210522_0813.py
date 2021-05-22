# Generated by Django 3.2.3 on 2021-05-22 08:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('looker', '0002_auto_20210516_1809'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='stockdata',
            options={'ordering': ['ticker']},
        ),
        migrations.AddField(
            model_name='stockdata',
            name='market',
            field=models.CharField(blank=True, help_text='Name of the market, options for now: SP500, Nasdaq and Dow', max_length=50),
        ),
        migrations.AlterField(
            model_name='stockdata',
            name='name',
            field=models.CharField(blank=True, help_text='Name of the bussiness', max_length=50),
        ),
    ]
