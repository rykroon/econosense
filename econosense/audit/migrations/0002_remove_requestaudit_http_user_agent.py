# Generated by Django 2.0.5 on 2018-05-21 00:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('audit', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='requestaudit',
            name='http_user_agent',
        ),
    ]
