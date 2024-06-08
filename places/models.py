from django.db import models
from django.utils import timezone


class Place(models.Model):
    address = models.TextField(
        'адрес',
        db_index=True,
        unique=True
    )

    latitude = models.DecimalField(
        'широта',
        max_digits=8,
        decimal_places=2,
        blank=True,
        null=True
    )
    longitude = models.DecimalField(
        'долгота',
        max_digits=8,
        decimal_places=2,
        blank=True,
        null=True
    )

    updated_at = models.DateTimeField(
        'Дата обновления',
        default=timezone.now
    )

    class Meta:
        verbose_name = 'Место'
        verbose_name_plural = 'Места'

    def __str__(self):
        return self.address
