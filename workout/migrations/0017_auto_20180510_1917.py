# Generated by Django 2.0.3 on 2018-05-10 18:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('workout', '0016_auto_20180509_0833'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='workout',
            options={'ordering': ['-date']},
        ),
    ]