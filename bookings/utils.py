from bookings.views import BookingViewSet
from .models import Booking
from rest_framework.routers import DefaultRouter
from .services import is_room_available
from datetime import date

def is_room_available(room, check_in, check_out):
    return not Booking.objects.filter(
        room=room,
        check_in__lt=check_out,
        check_out__gt=check_in
    ).exists()

# Example function that uses the service
def can_book_room(room_id, check_in, check_out):
    return is_room_available(room_id, check_in, check_out)
