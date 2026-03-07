import logging
import requests
from django.conf import settings

logger = logging.getLogger(__name__)


def send_whatsapp_receipt(customer, delivery):
    token = getattr(settings, "WHATSAPP_API_TOKEN", "")
    api_url = getattr(settings, "WHATSAPP_API_URL", "")

    phone = customer.phone.strip()
    if not phone.startswith("+"):
        if phone.startswith("0"):
            phone = phone[1:]
        phone = f"91{phone}"

    if not token or not api_url or "YOUR_PHONE_NUMBER_ID" in api_url:
        print(f"[WhatsApp DEV] To: {customer.name} ({phone}) | Jars: {delivery.jar_count} | Amount: Rs{delivery.amount}")
        return {"status": "dev_mode"}

    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    payload = {
        "messaging_product": "whatsapp",
        "to": phone,
        "type": "template",
        "template": {
            "name": "delivery_receipt",
            "language": {"code": "en"},
            "components": [{"type": "body", "parameters": [
                {"type": "text", "text": customer.name},
                {"type": "text", "text": str(delivery.jar_count)},
                {"type": "text", "text": str(delivery.amount)},
                {"type": "text", "text": delivery.get_payment_status_display()},
            ]}],
        },
    }
    try:
        resp = requests.post(api_url, json=payload, headers=headers, timeout=10)
        resp.raise_for_status()
        return {"status": "sent", "response": resp.json()}
    except requests.exceptions.RequestException as e:
        logger.error(f"WhatsApp error: {e}")
        return {"status": "error", "message": str(e)}
