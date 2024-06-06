from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Table(models.Model):
    title = models.CharField(max_length=255)
    available_seats = models.IntegerField(default=1,
                                          validators=[MaxValueValidator(100),
                                                      MinValueValidator(1)])
    description = models.TextField()
    price = models.IntegerField()

    def __str__(self):
        return f"{self.title}"


class Booking(models.Model):
    BOOKING_STATUS = (
        ('PAID', 'PAID'),
        ('CANCEL', 'CANCEL'),
        ('VERIFY', 'VERIFY'),
    )

    userID = models.ForeignKey('Account', on_delete=models.PROTECT, null=False, blank=False)

    status = models.CharField(max_length=6, choices=BOOKING_STATUS)
    tableID = models.ForeignKey('Table', on_delete=models.PROTECT, null=False, blank=False)
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    occupied_seats = models.IntegerField(
        default=0,
        validators=[MaxValueValidator(100),
                    MinValueValidator(1)]
    )
