import pytest
import time
from unittest.mock import AsyncMock, patch, MagicMock
import httpx
from app.core.config import settings
from app.services.paypal_service import PayPalService
from app.main import app

@pytest.fixture(autouse=True)
def reset_paypal_token_cache():
    """Reset cached token before each test."""
    PayPalService._cached_token = None
    PayPalService._token_expiry_timestamp = 0
    yield
    PayPalService._cached_token = None
    PayPalService._token_expiry_timestamp = 0


@pytest.mark.asyncio
async def test_paypal_service_requires_credentials_when_mock_mode_disabled():
    """In sandbox mode with mock mode disabled, missing credentials must raise ValueError."""
    with patch.object(settings, "PAYPAL_MOCK_MODE", False), \
         patch.object(settings, "PAYPAL_CLIENT_ID", ""), \
         patch.object(settings, "PAYPAL_CLIENT_SECRET", ""):
        
        with pytest.raises(ValueError, match="PayPal credentials not configured"):
            await PayPalService.get_access_token()


@pytest.mark.asyncio
async def test_oauth2_token_retrieval_and_caching():
    """Verify OAuth2 client-credentials flow caches token and avoids duplicate requests."""
    with patch.object(settings, "PAYPAL_MOCK_MODE", False), \
         patch.object(settings, "PAYPAL_CLIENT_ID", "test_client_id_123"), \
         patch.object(settings, "PAYPAL_CLIENT_SECRET", "test_client_secret_456"):

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "access_token": "ACCESS_TOKEN_XYZ_999",
            "token_type": "Bearer",
            "expires_in": 3600
        }

        mock_client = AsyncMock()
        mock_client.post.return_value = mock_response

        with patch("httpx.AsyncClient") as mock_client_cls:
            mock_client_cls.return_value.__aenter__.return_value = mock_client

            # First retrieval - should make HTTP call
            token1 = await PayPalService.get_access_token()
            assert token1 == "ACCESS_TOKEN_XYZ_999"
            assert mock_client.post.call_count == 1

            # Second retrieval - should use cached token without additional HTTP call
            token2 = await PayPalService.get_access_token()
            assert token2 == "ACCESS_TOKEN_XYZ_999"
            assert mock_client.post.call_count == 1  # Still 1, cached!


@pytest.mark.asyncio
async def test_oauth2_token_refreshes_near_expiry():
    """Verify OAuth2 token is refreshed if within 300s buffer of expiration."""
    with patch.object(settings, "PAYPAL_MOCK_MODE", False), \
         patch.object(settings, "PAYPAL_CLIENT_ID", "test_client_id_123"), \
         patch.object(settings, "PAYPAL_CLIENT_SECRET", "test_client_secret_456"):

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "access_token": "NEW_REFRESHED_TOKEN",
            "token_type": "Bearer",
            "expires_in": 3600
        }

        # Simulate existing token expiring in 100 seconds (< 300 buffer)
        PayPalService._cached_token = "OLD_EXPIRING_TOKEN"
        PayPalService._token_expiry_timestamp = time.time() + 100

        mock_client = AsyncMock()
        mock_client.post.return_value = mock_response

        with patch("httpx.AsyncClient") as mock_client_cls:
            mock_client_cls.return_value.__aenter__.return_value = mock_client

            token = await PayPalService.get_access_token()
            assert token == "NEW_REFRESHED_TOKEN"
            assert mock_client.post.call_count == 1


@pytest.mark.asyncio
async def test_create_order_against_orders_v2_api():
    """Verify create_order builds correct payload and parses Orders API v2 response."""
    with patch.object(settings, "PAYPAL_MOCK_MODE", False), \
         patch.object(settings, "PAYPAL_CLIENT_ID", "client_123"), \
         patch.object(settings, "PAYPAL_CLIENT_SECRET", "secret_456"), \
         patch.object(PayPalService, "get_access_token", AsyncMock(return_value="VALID_TOKEN")):

        mock_order_response = MagicMock()
        mock_order_response.status_code = 201
        mock_order_response.json.return_value = {
            "id": "REAL_SANDBOX_ORDER_789",
            "status": "CREATED",
            "links": [
                {"rel": "approve", "href": "https://www.sandbox.paypal.com/checkoutnow?token=REAL_SANDBOX_ORDER_789"},
                {"rel": "self", "href": "https://api-m.sandbox.paypal.com/v2/checkout/orders/REAL_SANDBOX_ORDER_789"}
            ]
        }

        mock_client = AsyncMock()
        mock_client.post.return_value = mock_order_response

        with patch("httpx.AsyncClient") as mock_client_cls:
            mock_client_cls.return_value.__aenter__.return_value = mock_client

            result = await PayPalService.create_order(
                amount_usd=42.50,
                reference_id="ref_payment_001",
                description="AI Agent marketplace settlement"
            )

            assert result["id"] == "REAL_SANDBOX_ORDER_789"
            assert result["status"] == "CREATED"
            assert len(result["links"]) == 2

            # Inspect payload passed to Orders API v2
            sent_payload = mock_client.post.call_args[1]["json"]
            assert sent_payload["intent"] == "CAPTURE"
            unit = sent_payload["purchase_units"][0]
            assert unit["amount"]["value"] == "42.50"
            assert unit["amount"]["currency_code"] == "USD"
            assert unit["custom_id"] == "ref_payment_001"


@pytest.mark.asyncio
async def test_capture_order_parsing_orders_v2():
    """Verify capture_order parses PayPal COMPLETED response with capture ID."""
    with patch.object(settings, "PAYPAL_MOCK_MODE", False), \
         patch.object(settings, "PAYPAL_CLIENT_ID", "client_123"), \
         patch.object(settings, "PAYPAL_CLIENT_SECRET", "secret_456"), \
         patch.object(PayPalService, "get_access_token", AsyncMock(return_value="VALID_TOKEN")):

        mock_capture_response = MagicMock()
        mock_capture_response.status_code = 201
        mock_capture_response.json.return_value = {
            "id": "SANDBOX_ORDER_111",
            "status": "COMPLETED",
            "purchase_units": [
                {
                    "payments": {
                        "captures": [
                            {
                                "id": "REAL_CAPTURE_ID_999",
                                "status": "COMPLETED",
                                "amount": {
                                    "value": "42.50",
                                    "currency_code": "USD"
                                }
                            }
                        ]
                    }
                }
            ]
        }

        mock_client = AsyncMock()
        mock_client.post.return_value = mock_capture_response

        with patch("httpx.AsyncClient") as mock_client_cls:
            mock_client_cls.return_value.__aenter__.return_value = mock_client

            result = await PayPalService.capture_order("SANDBOX_ORDER_111")
            assert result["id"] == "SANDBOX_ORDER_111"
            assert result["status"] == "COMPLETED"
            captures = result["purchase_units"][0]["payments"]["captures"]
            assert captures[0]["id"] == "REAL_CAPTURE_ID_999"
            assert captures[0]["status"] == "COMPLETED"
            assert captures[0]["amount"]["value"] == "42.50"
            assert captures[0]["amount"]["currency_code"] == "USD"


@pytest.mark.asyncio
async def test_webhook_signature_verification():
    """Verify webhook signature verification uses PayPal /v1/notifications/verify-webhook-signature."""
    with patch.object(settings, "PAYPAL_MOCK_MODE", False), \
         patch.object(settings, "PAYPAL_CLIENT_ID", "client_123"), \
         patch.object(settings, "PAYPAL_CLIENT_SECRET", "secret_456"), \
         patch.object(settings, "PAYPAL_WEBHOOK_ID", "WH-GENUINE-ID"), \
         patch.object(PayPalService, "get_access_token", AsyncMock(return_value="VALID_TOKEN")):

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"verification_status": "SUCCESS"}

        mock_client = AsyncMock()
        mock_client.post.return_value = mock_response

        with patch("httpx.AsyncClient") as mock_client_cls:
            mock_client_cls.return_value.__aenter__.return_value = mock_client

            is_valid = await PayPalService.verify_webhook_signature(
                transmission_id="trans_123",
                transmission_time="2026-11-06T00:00:00Z",
                cert_url="https://api.sandbox.paypal.com/v1/notifications/certs/CERT-123",
                auth_algo="SHA256withRSA",
                transmission_sig="signature_string",
                webhook_body={"event_type": "CHECKOUT.ORDER.COMPLETED", "resource": {"id": "ORDER_1"}},
            )
            assert is_valid is True

            # Verify failure path
            mock_response.json.return_value = {"verification_status": "FAILURE"}
            is_invalid = await PayPalService.verify_webhook_signature(
                transmission_id="trans_123",
                transmission_time="2026-11-06T00:00:00Z",
                cert_url="https://api.sandbox.paypal.com/v1/notifications/certs/CERT-123",
                auth_algo="SHA256withRSA",
                transmission_sig="signature_string",
                webhook_body={"event_type": "CHECKOUT.ORDER.COMPLETED", "resource": {"id": "ORDER_1"}},
            )
            assert is_invalid is False


@pytest.mark.asyncio
async def test_webhook_endpoint_rejects_missing_headers():
    """Test webhook endpoint rejects requests missing required verification headers."""
    with patch.object(settings, "PAYPAL_MOCK_MODE", False):
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
            res = await client.post(
                "/api/v1/payments/webhook",
                json={"event_type": "PAYMENT.CAPTURE.COMPLETED"},
                headers={}  # Missing all PayPal headers
            )
            assert res.status_code == 400
            assert "Missing required PayPal transmission verification headers" in res.json()["detail"]
