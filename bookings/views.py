# bookings/views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from .serializers import BookingSerializer
from rooms.models import Room  # make sure this is correct

@api_view(['POST'])
@permission_classes([AllowAny])
def create_public_booking(request):
    serializer = BookingSerializer(data=request.data)

    if serializer.is_valid():
        validated_data = serializer.validated_data
        room = Room.objects.get(pk=validated_data['room'].id)
        price = room.price_per_night

        # calculate total_price
        check_in = serializer.validated_data['check_in']
        check_out = serializer.validated_data['check_out']
        nights = (check_out - check_in).days
        total_price = nights * room.price_per_night

        # save booking
        booking = serializer.save(total_price=price * validated_data.get('nights', 1))

        return Response({
            "message": "Booking created successfully",
            "booking_id": booking.id,
            "nights": booking.nights,
            "total_price": booking.total_price
        }, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
# bookings/views.py
"""from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status

from .serializers import BookingSerializer

@api_view(['POST'])
@permission_classes([AllowAny])  # 🔓 PUBLIC
def create_public_booking(request):
    serializer = BookingSerializer(data=request.data)
    room = Room.objects.get(pk=validated_data['room'])
    price = room.price_per_night

    if serializer.is_valid():
        booking = serializer.save()
        return Response({
            "message": "Booking created successfully",
            "booking_id": booking.id,
            "nights": booking.nights,
            "total_price": booking.total_price
        }, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)"""
