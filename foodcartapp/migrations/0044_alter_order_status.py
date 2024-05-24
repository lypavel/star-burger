# Generated by Django 3.2.15 on 2024-05-24 19:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0043_order_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('Создан', 'Создан'), ('Подтверждён', 'Подтверждён'), ('Доставляется', 'Доставляется'), ('Завершён', 'Завершён')], db_index=True, default='Создан', max_length=50, verbose_name='статус'),
        ),
    ]
