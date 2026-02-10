"""from rest_framework import serializers
from .models import Booking
from .services import is_room_available
from datetime import timedelta"""

"""class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = '__all__'
        read_only_fields = ('amount', 'nights', 'user')

    def validate(self, data):
        if not is_room_available(
            data['room'], data['check_in'], data['check_out']
        ):
            raise serializers.ValidationError("Room not available")
        return data

    def create(self, validated_data):
        request = self.context['request']
        room = validated_data['room']
        check_in = validated_data['check_in']
        check_out = validated_data['check_out']

        nights = (check_out - check_in).days
        amount = nights * room.price_per_night

        booking = Booking.objects.create(
            user=request.user,
            room=room,
            check_in=check_in,
            check_out=check_out,
            nights=nights,
            amount=amount,
            status='confirmed'
        )

        # Update room status
        room.status = 'occupied'
        room.save()

        return booking"""
        
# bookings/serializers.py
from rest_framework import serializers
from .models import Booking

class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = [
            'room',
            'guest_name',
            'guest_email',
            'check_in',
            'check_out',
            'nights',
            'total_price',
        ]
        read_only_fields = ['nights','total_price']

    def validate(self, data):
        if data['check_out'] <= data['check_in']:
            raise serializers.ValidationError(
                "Check-out date must be after check-in date"
            )
        return data

