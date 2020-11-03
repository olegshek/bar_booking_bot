# Generated by Django 3.1.2 on 2020-11-02 08:20

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Feedback',
            fields=[
                ('book_request', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='feedback', serialize=False, to='customer.bookrequest', verbose_name='Book request')),
                ('text', models.CharField(max_length=4096, verbose_name='Text')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
    ]