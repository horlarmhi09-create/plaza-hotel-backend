"""from django.shortcuts import get_object_or_404
import uuid
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from bookings.models import Booking
from .models import Payment
from .paystack import initialize_payment, verify_payment

class InitializePaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        print("Request data:", request.data)
        booking_id = request.data.get("booking_id")
        if not booking_id:
            return Response({"error": "booking_id is required"}, status=400)

        booking = get_object_or_404(Booking, id=booking_id)

        reference = str(uuid.uuid4())

        amount = booking.room.price_per_night or 0
        payment = Payment.objects.create(
            booking=booking,
            reference=reference,
            amount=amount,
            status="pending"
        )

        # Call Paystack
        response = initialize_payment(
            email=request.user.email,
            amount=payment.amount,
            reference=reference
        )

        # Check if 'data' exists
        if not response.get("data"):
            return Response({
                "error": "Paystack returned an error",
                "response": response
            }, status=502)

        return Response({
            "authorization_url": response["data"]["authorization_url"],
            "reference": reference
        })"""



"""from django.shortcuts import get_object_or_404
from .models import Payment
from .paystack import verify_payment

class VerifyPaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        reference = request.query_params.get("reference")
        if not reference:
            return Response({"message": "Reference is required"}, status=400)

        # Safely get the payment
        payment = get_object_or_404(Payment, reference=reference)

        # Call Paystack API
        response = verify_payment(reference)

        # Check if Paystack returned a valid response
        if not response.get("status") or not response.get("data"):
            return Response({
                "message": "Paystack verification failed",
                "response": response
            }, status=400)

        paystack_status = response["data"].get("status")
        if paystack_status == "success":
            payment.status = "successful"
            payment.save()

            booking = payment.booking
            booking.status = "confirmed"
            booking.save()

            return Response({"message": "Payment successful"})

        else:
            payment.status = "failed"
            payment.save()
            return Response({"message": "Payment failed"}, status=400)"""
            
"""from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Booking
from .paystack import initialize_payment, verify_payment

@api_view(['POST'])
@permission_classes([AllowAny])
def initialize_payment(request):
    booking_id = request.data.get('booking_id')
    email = request.data.get('email')

    if not booking_id or not email:
        return Response(
            {"error": "booking_id and email are required"},
            status=400
        )

    booking = get_object_or_404(Booking, id=booking_id)

    amount = booking.total_amount  # make sure this field exists

    payment_url = initialize_payment(
        email=email,
        amount=amount,
        reference=str(booking.id)
    )

    return Response({
        "payment_url": payment_url
    })"""

# payments/views.py
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.shortcuts import get_object_or_404, redirect
from .models import Payment
from .serializers import PaymentSerializer
from .paystack import initialize_payment, verify_payment
from decimal import Decimal
from bookings.models import Booking
from rest_framework.permissions import IsAdminUser
from drf_spectacular.utils import extend_schema
from .serializers import (
    PaymentSerializer,
    InitializePaymentRequestSerializer,
    VerifyPaymentRequestSerializer
)
import uuid
import hmac
import hashlib
import json
from django.http import HttpResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail


class InitializePaymentView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        request=InitializePaymentRequestSerializer,
        responses={200: None},
        auth=[]
    )
    def post(self, request):
        booking_id = request.data.get('booking_id')
        email = request.data.get('email')

        if not booking_id or not email:
            return Response({"error": "booking_id and email are required"}, status=400)

        booking = get_object_or_404(Booking, id=booking_id)

        amount_in_kobo = int(booking.total_price * 100)

        booking.status = 'pending'
        booking.save()

        booking.room.status = 'pending'
        booking.room.save()

        print("TOTAL PRICE:", booking.total_price)
        print("AMOUNT IN KOBO:", amount_in_kobo)

        if amount_in_kobo <= 0:
            return Response({"error": "Amount must be greater than zero"}, status=400)

        # ✅ Generate unique reference
        reference = f"BOOK-{booking.id}-{uuid.uuid4().hex[:8]}"
    
        booking.reference = reference
        booking.save()

        payment_url = initialize_payment(
            email=email,
            amount=amount_in_kobo,
            reference=reference,
            callback_url="https://api.blissfulplace.com.ng/paymentCallback/"
        )

        return Response({
            "authorization_url": payment_url,
            "reference": reference
        })



class VerifyPaymentView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        request=VerifyPaymentRequestSerializer,
        responses={200: None},
        auth=[]
    )
    def post(self, request):
        reference = request.data.get('reference')
        booking_id = request.data.get('booking_id')  # You need to know which booking

        if not reference or not booking_id:
            return Response({"error": "reference and booking_id are required"}, status=400)

        # Call your existing verify_payment function
        success, amount = verify_payment(reference)  # Modify your verify_payment to return amount too

        try:
            booking = Booking.objects.get(id=booking_id)
        except Booking.DoesNotExist:
            return Response({"error": "Booking not found"}, status=404)

        # Save or update payment record
        payment, created = Payment.objects.update_or_create(
            reference=reference,
            defaults={
                "booking": booking,
                "status": "successful" if success else "failed",
                "amount": amount if amount else 0.0
            }
        )

        if success:
            booking.status = "confirmed"
            booking.room.status = "booked"
        else:
            booking.status = "cancelled"
            booking.room.status = "available"

        booking.save()
        booking.room.save()

        return Response({
            "success": success,
            "payment_id": payment.id,
            "status": payment.status,
            "room_status": booking.room.status if success else None
        })

class PaymentListView(APIView):
    permission_classes = [IsAdminUser]  # Only admin/dashboard can see
    @extend_schema(
        request=VerifyPaymentRequestSerializer,
        responses={200: None},
        auth=[]
    )
    def get(self, request):
        payments = Payment.objects.all().order_by('-created_at')
        serializer = PaymentSerializer(payments, many=True)
        return Response(serializer.data)

def payment_callback(request):
    reference = request.GET.get("reference")

    # Redirect to frontend page
    return redirect(f"https://blissfulplace.ng/payment-success?reference={reference}")

"""@csrf_exempt
def paystack_webhook(request):
    payload = request.body
    signature = request.headers.get("x-paystack-signature")

    computed_signature = hmac.new(
        settings.PAYSTACK_SECRET_KEY.encode(),
        payload,
        hashlib.sha512
    ).hexdigest()

    if computed_signature != signature:
        return HttpResponse(status=400)

    event = json.loads(payload)

    if event["event"] == "charge.success":
        data = event["data"]
        reference = data["reference"]
        amount = data["amount"] / 100
        email = data["customer"]["email"]

        if Payment.objects.filter(reference=reference).exists():
            return HttpResponse(status=200)

        # Find the booking using payment_reference
        booking = Booking.objects.get(reference=reference)

        Payment.objects.create(
            booking=booking,
            reference=reference,
            amount=amount,
            email=email,
            status="success",
            paid_at=data["paid_at"]
        )
        booking.status = "confirmed"
        booking.payment_status = "paid"
        booking.save()

        # ✅ Update the room
        room = booking.room
        room.status = "booked"
        room.save()

        send_mail(
            "Booking Confirmed",
            f"Your booking at Blissful Place has been confirmed.",
            settings.DEFAULT_FROM_EMAIL,
            [email],
        )

    return HttpResponse(status=200)"""
