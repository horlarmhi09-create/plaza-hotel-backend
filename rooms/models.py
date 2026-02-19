from django.db import models

class Room(models.Model):
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('booked', 'Booked'),
        ('pending', 'Pending'),
        ('maintenance', 'Maintenance'),
    ]

    ROOM_TYPE_CHOICES = [
        ('deluxe_suite', 'Deluxe Suite'),
        ('executive_suite', 'Executive Suite'),
        ('presidential_suite', 'Presidential Suite'),
    ]

    room_number = models.CharField(max_length=20, null=True, blank=True)
    room_type = models.CharField(max_length=50, choices=ROOM_TYPE_CHOICES, default='deluxe_suite')
    description = models.TextField(default='A cozy room perfect for your stay.')
    price = models.DecimalField(max_digits=10, decimal_places=2, default=10000)
    image = models.ImageField(upload_to='rooms/', null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Room {self.room_number} ({self.get_room_type_display()})"
