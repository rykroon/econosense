# Generated by Django 2.0.7 on 2018-07-22 23:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0007_auto_20180717_1752'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tax',
            name='state_tax',
            field=models.DecimalField(decimal_places=2, max_digits=8, null=True),
        ),
    ]