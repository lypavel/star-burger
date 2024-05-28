# Generated by Django 3.2.15 on 2024-05-28 11:25

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Place',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('address', models.TextField(db_index=True, unique=True, verbose_name='адрес')),
                ('latitude', models.DecimalField(blank=True, decimal_places=2, max_digits=8, verbose_name='ширина')),
                ('longtitude', models.DecimalField(blank=True, decimal_places=2, max_digits=8, verbose_name='долгота')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Дата обновления')),
            ],
            options={
                'verbose_name': 'Место',
                'verbose_name_plural': 'Места',
            },
        ),
    ]