# Generated by Django 3.1.2 on 2020-10-28 07:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0003_auto_20201028_1237'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='weekday',
            options={'ordering': ('id',)},
        ),
    ]
