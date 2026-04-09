from rest_framework import serializers
from .models import Payment

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['id', 'booking', 'reference', 'amount', 'status', 'created_at']

class InitializePaymentRequestSerializer(serializers.Serializer):
    booking_id = serializers.IntegerField()
    email = serializers.EmailField()


class VerifyPaymentRequestSerializer(serializers.Serializer):
    reference = serializers.CharField()
    booking_id = serializers.IntegerField()
