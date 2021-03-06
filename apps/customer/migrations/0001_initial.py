# Generated by Django 3.1.2 on 2020-10-27 09:29

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='BlockedUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone_number', models.CharField(max_length=15, unique=True, verbose_name='Phone number')),
            ],
            options={
                'verbose_name': 'Blocked user',
                'verbose_name_plural': 'Blocked users',
            },
        ),
        migrations.CreateModel(
            name='Gender',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=6, verbose_name='Name')),
                ('text', models.CharField(max_length=10, null=True, verbose_name='Text')),
                ('text_ru', models.CharField(max_length=10, null=True, verbose_name='Text')),
                ('text_en', models.CharField(max_length=10, null=True, verbose_name='Text')),
            ],
        ),
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.IntegerField(editable=False, primary_key=True, serialize=False, unique=True)),
                ('username', models.CharField(blank=True, max_length=20, null=True)),
                ('full_name', models.CharField(blank=True, max_length=200, null=True, verbose_name='Full name')),
                ('phone_number', models.CharField(max_length=20, null=True, verbose_name='Phone number')),
                ('age', models.IntegerField(null=True, verbose_name='Age')),
                ('related_people', models.TextField(null=True, verbose_name='Related people')),
                ('is_blocked', models.BooleanField(default=False, verbose_name='Is blocked')),
                ('language', models.CharField(choices=[('ru', 'Russian'), ('en', 'English')], max_length=2, null=True, verbose_name='Language')),
                ('gender', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='customers', to='customer.gender', verbose_name='Gender')),
            ],
            options={
                'verbose_name': 'Customer',
                'verbose_name_plural': 'Customers',
            },
        ),
        migrations.CreateModel(
            name='BookRequest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('book_id', models.IntegerField(null=True)),
                ('datetime', models.DateTimeField(null=True, verbose_name='Datetime')),
                ('people_quantity', models.IntegerField(null=True, verbose_name='People quantity')),
                ('confirmed_at', models.DateTimeField(null=True, verbose_name='Confirmed at')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Created at')),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='book_requests', to='customer.customer', verbose_name='Customer')),
            ],
            options={
                'verbose_name': 'Book request',
                'verbose_name_plural': 'Book requests',
                'ordering': ('-confirmed_at',),
            },
        ),
    ]
