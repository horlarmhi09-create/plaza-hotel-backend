# payments/paystack.py
import requests
from django.conf import settings

PAYSTACK_SECRET_KEY = "sk_test_dc72e4ed648951b7988cf5bc13b9bebf83d6cd96"

BASE_URL = "https://api.paystack.co"

def initialize_payment(email: str, amount: int, reference: str) -> str:
    """
    Initialize a Paystack payment.
    amount should be in kobo (1 NGN = 100 kobo)
    Returns the authorization URL for the frontend.
    """
    url = f"{BASE_URL}/transaction/initialize"
    headers = {
        "Authorization": f"Bearer {PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "email": email,
        "amount": amount,
        "reference": reference,
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        data = response.json()
        if data.get("status") is True:
            return data["data"]["authorization_url"]
        else:
            return {"error": data.get("message", "Initialization failed")}
    except Exception as e:
        return {"error": str(e)}


def verify_payment(reference: str) -> tuple[bool, int]:
    """
    Verify a Paystack payment by reference.
    Returns a tuple (success: bool, amount: int_in_naira)
    """
    url = f"{BASE_URL}/transaction/verify/{reference}"
    headers = {"Authorization": f"Bearer {PAYSTACK_SECRET_KEY}"}

    try:
        response = requests.get(url, headers=headers)
        data = response.json().get("data", {})
        success = data.get("status") == "success"
        # Paystack returns amount in kobo, convert to Naira
        amount = int(data.get("amount", 0)) / 100
        return success, amount
    except Exception as e:
        return False, 0

