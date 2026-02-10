from django.db import models
from django.utils import timezone
# Create your models hefrom django.db import models
from accounts.models import User
from rooms.models import Room
"""class Booking(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('checked_in', 'Checked In'),
        ('checked_out', 'Checked Out'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    check_in = models.DateField()
    check_out = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user} - {self.room} - ₦{self.amount}"""
    
    
from django.db import models
from rooms.models import Room
from datetime import date

class Booking(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)

    guest_name = models.CharField(max_length=100)
    guest_email = models.EmailField()
    guest_phone = models.CharField(max_length=20, blank=True)

    check_in = models.DateField()
    check_out = models.DateField()

    nights = models.PositiveIntegerField(null=True, blank=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.check_in and self.check_out:
            self.nights = (self.check_out - self.check_in).days

            if self.nights <= 0:
                raise ValueError("Check-out date must be after check-in date")

            self.total_price = self.room.price_per_night * self.nights

            super().save(*args, **kwargs)




