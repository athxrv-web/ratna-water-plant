def send_whatsapp_receipt(customer, amount):
    """
    Placeholder for WhatsApp Business API integration.

    In production, replace this with an actual API call to:
    - WhatsApp Business API (official)
    - Twilio WhatsApp
    - Any other WhatsApp gateway

    For now, it just prints to the console.
    """
    print(
        f"[WhatsApp Receipt] "
        f"To: {customer.name} ({customer.phone}) | "
        f"Amount: ₹{amount:.2f} | "
        f"Message: Thank you for your order from Ratna Water Plant!"
    )