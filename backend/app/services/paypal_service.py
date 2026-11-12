import base64
import time
from typing import Any, Dict, Optional
import httpx
from app.core.config import settings


class PayPalService:
    _cached_token: Optional[str] = None
    _token_expiry_timestamp: float = 0.0
    _mock_orders: Dict[str, float] = {}

    @classmethod
    def _validate_credentials_configured(cls) -> None:
        """Validates that PayPal Sandbox credentials are provided when mock mode is disabled."""
        if not settings.PAYPAL_MOCK_MODE:
            if not settings.PAYPAL_CLIENT_ID or not settings.PAYPAL_CLIENT_SECRET:
                raise ValueError(
                    "PayPal credentials not configured: PAYPAL_CLIENT_ID and PAYPAL_CLIENT_SECRET "
                    "are required when PAYPAL_MOCK_MODE=false"
                )

    @classmethod
    def clear_token_cache(cls) -> None:
        """Clears the cached access token (useful in tests)."""
        cls._cached_token = None
        cls._token_expiry_timestamp = 0.0

    @classmethod
    async def get_access_token(cls) -> str:
        """
        Retrieves and caches OAuth2 Bearer token from PayPal Sandbox.
        Caches token until 5 minutes (300 seconds) prior to expiration.
        """
        now = time.time()
        if cls._cached_token and now < (cls._token_expiry_timestamp - 300):
            return cls._cached_token

        # If mock mode is explicitly enabled for unit tests
        if settings.PAYPAL_MOCK_MODE:
            cls._cached_token = "mock_paypal_access_token_unit_test"
            cls._token_expiry_timestamp = now + 3600
            return cls._cached_token

        cls._validate_credentials_configured()

        auth_header = base64.b64encode(
            f"{settings.PAYPAL_CLIENT_ID}:{settings.PAYPAL_CLIENT_SECRET}".encode("utf-8")
        ).decode("utf-8")

        url = f"{settings.PAYPAL_BASE_URL}/v1/oauth2/token"
        headers = {
            "Authorization": f"Basic {auth_header}",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        data = {"grant_type": "client_credentials"}

        async with httpx.AsyncClient(timeout=20.0) as client:
            resp = await client.post(url, headers=headers, data=data)
            if resp.status_code != 200:
                raise RuntimeError(
                    f"PayPal OAuth2 authentication failed [{resp.status_code}]: {resp.text}"
                )
            payload = resp.json()
            access_token = payload.get("access_token")
            if not access_token:
                raise RuntimeError(f"PayPal OAuth2 response missing access_token: {payload}")

            cls._cached_token = access_token
            expires_in = float(payload.get("expires_in", 3600))
            cls._token_expiry_timestamp = now + expires_in
            return cls._cached_token

    @classmethod
    async def create_order(
        cls,
        amount_usd: float,
        reference_id: str,
        description: str,
        custom_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Creates an order via PayPal Orders API v2 (intent=CAPTURE).
        Returns the parsed PayPal response containing the real PayPal Order ID.
        """
        # Unit test mock mode check
        if settings.PAYPAL_MOCK_MODE:
            mock_order_id = f"5O{int(time.time()*1000)}"[:17]
            cls._mock_orders[mock_order_id] = amount_usd
            return {
                "id": mock_order_id,
                "status": "CREATED",
                "intent": "CAPTURE",
                "links": [
                    {
                        "href": f"https://www.sandbox.paypal.com/checkoutnow?token={mock_order_id}",
                        "rel": "approve",
                        "method": "GET",
                    }
                ],
                "purchase_units": [
                    {
                        "reference_id": reference_id,
                        "description": description,
                        "custom_id": custom_id,
                        "amount": {
                            "currency_code": "USD",
                            "value": f"{amount_usd:.2f}",
                        },
                    }
                ],
            }

        token = await cls.get_access_token()
        url = f"{settings.PAYPAL_BASE_URL}/v2/checkout/orders"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Prefer": "return=representation",
        }
        body = {
            "intent": "CAPTURE",
            "purchase_units": [
                {
                    "reference_id": reference_id,
                    "description": description,
                    "custom_id": custom_id or reference_id,
                    "amount": {
                        "currency_code": "USD",
                        "value": f"{amount_usd:.2f}",
                    },
                }
            ],
            "application_context": {
                "brand_name": "The AI Economy",
                "landing_page": "NO_PREFERENCE",
                "user_action": "PAY_NOW",
                "return_url": f"{settings.FRONTEND_URL}/payment/success",
                "cancel_url": f"{settings.FRONTEND_URL}/payment/cancel",
            },
        }

        async with httpx.AsyncClient(timeout=25.0) as client:
            resp = await client.post(url, headers=headers, json=body)
            if resp.status_code not in (200, 201):
                raise RuntimeError(
                    f"PayPal Order Creation failed [{resp.status_code}]: {resp.text}"
                )
            order_data = resp.json()
            if not order_data.get("id"):
                raise RuntimeError(f"PayPal Order Creation response missing 'id': {order_data}")
            return order_data

    @classmethod
    async def capture_order(cls, order_id: str) -> Dict[str, Any]:
        """
        Captures payment for an approved PayPal order via POST /v2/checkout/orders/{id}/capture.
        Returns the parsed PayPal response containing capture ID, status, and amount.
        """
        # Unit test mock mode check
        if settings.PAYPAL_MOCK_MODE:
            mock_capture_id = f"3C{int(time.time()*1000)}"[:17]
            mock_amount = cls._mock_orders.get(order_id, 23.50)
            return {
                "id": order_id,
                "status": "COMPLETED",
                "purchase_units": [
                    {
                        "payments": {
                            "captures": [
                                {
                                    "id": mock_capture_id,
                                    "status": "COMPLETED",
                                    "amount": {
                                        "currency_code": "USD",
                                        "value": f"{mock_amount:.2f}",
                                    },
                                }
                            ]
                        }
                    }
                ],
            }

        token = await cls.get_access_token()
        url = f"{settings.PAYPAL_BASE_URL}/v2/checkout/orders/{order_id}/capture"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Prefer": "return=representation",
        }

        async with httpx.AsyncClient(timeout=25.0) as client:
            resp = await client.post(url, headers=headers, json={})
            if resp.status_code not in (200, 201):
                raise RuntimeError(
                    f"PayPal Order Capture failed [{resp.status_code}]: {resp.text}"
                )
            capture_data = resp.json()
            return capture_data

    @classmethod
    async def verify_webhook_signature(
        cls,
        transmission_id: str,
        transmission_time: str,
        cert_url: str,
        auth_algo: str,
        transmission_sig: str,
        webhook_body: dict,
    ) -> bool:
        """
        Validates webhook signature against PayPal Sandbox using:
        POST /v1/notifications/verify-webhook-signature
        """
        # Unit test mock mode check
        if settings.PAYPAL_MOCK_MODE:
            return True

        if not settings.PAYPAL_WEBHOOK_ID:
            raise ValueError(
                "PAYPAL_WEBHOOK_ID is not configured: required for webhook signature verification"
            )

        token = await cls.get_access_token()
        url = f"{settings.PAYPAL_BASE_URL}/v1/notifications/verify-webhook-signature"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        body = {
            "transmission_id": transmission_id,
            "transmission_time": transmission_time,
            "cert_url": cert_url,
            "auth_algo": auth_algo,
            "transmission_sig": transmission_sig,
            "webhook_id": settings.PAYPAL_WEBHOOK_ID,
            "webhook_event": webhook_body,
        }

        async with httpx.AsyncClient(timeout=20.0) as client:
            resp = await client.post(url, headers=headers, json=body)
            if resp.status_code == 200:
                result = resp.json()
                return result.get("verification_status") == "SUCCESS"
            return False
