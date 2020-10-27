# Generated by Django 3.1.2 on 2020-10-23 07:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Button',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True, verbose_name='Name')),
                ('text', models.CharField(max_length=50, unique=True, verbose_name='Text')),
                ('text_ru', models.CharField(max_length=50, null=True, unique=True, verbose_name='Text')),
                ('text_en', models.CharField(max_length=50, null=True, unique=True, verbose_name='Text')),
            ],
            options={
                'verbose_name': 'Button',
                'verbose_name_plural': 'Buttons',
            },
        ),
        migrations.CreateModel(
            name='Keyboard',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True, verbose_name='Name')),
            ],
            options={
                'verbose_name': 'Keyboard',
                'verbose_name_plural': 'Keyboards',
            },
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100, unique=True, verbose_name='Title')),
                ('text', models.TextField()),
                ('text_ru', models.TextField(null=True)),
                ('text_en', models.TextField(null=True)),
            ],
            options={
                'verbose_name': 'Message',
                'verbose_name_plural': 'Messages',
            },
        ),
        migrations.CreateModel(
            name='KeyboardButtonsOrdering',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ordering', models.PositiveIntegerField(verbose_name='Ordering')),
                ('button', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ordering', to='bot.button', verbose_name='Keyboard')),
                ('keyboard', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='buttons_ordering', to='bot.keyboard', verbose_name='Keyboard')),
            ],
            options={
                'verbose_name': 'Keyboard buttons ordering',
                'verbose_name_plural': 'Keyboard buttons orderings',
            },
        ),
        migrations.AddField(
            model_name='keyboard',
            name='buttons',
            field=models.ManyToManyField(related_name='keyboards', through='bot.KeyboardButtonsOrdering', to='bot.Button', verbose_name='Buttons'),
        ),
    ]
