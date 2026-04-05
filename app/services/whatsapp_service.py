import logging

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


def send_whatsapp(
    owner_phone: str,
    vehicle_number: str,
    message: str = "",
) -> dict:
    """
    Send a masked WhatsApp message to the vehicle owner via business number.

    Mock implementation for MVP — logs the message and returns success.
    Replace with real WhatsApp Business API (Meta Cloud API) for production.

    Production integration:
      POST https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages
      Headers: Authorization: Bearer {WHATSAPP_API_TOKEN}
      Body: {
        "messaging_product": "whatsapp",
        "to": owner_phone,
        "type": "template",
        "template": {
          "name": "vehicle_contact",
          "language": {"code": "en"},
          "components": [{"type": "body", "parameters": [...]}]
        }
      }
    """
    default_msg = f"Someone is trying to reach you regarding your vehicle {vehicle_number}. Please check your car."
    final_message = message or default_msg

    logger.info(
        "WhatsApp sent: owner=%s, vehicle=%s, msg='%s' (MOCK)",
        owner_phone,
        vehicle_number,
        final_message,
    )

    # --- Real WhatsApp Business API (uncomment when ready) ---
    # import requests
    # response = requests.post(
    #     f"https://graph.facebook.com/v18.0/{settings.WHATSAPP_PHONE_NUMBER_ID}/messages",
    #     headers={
    #         "Authorization": f"Bearer {settings.WHATSAPP_API_TOKEN}",
    #         "Content-Type": "application/json",
    #     },
    #     json={
    #         "messaging_product": "whatsapp",
    #         "to": owner_phone,
    #         "type": "template",
    #         "template": {
    #             "name": "vehicle_contact",
    #             "language": {"code": "en"},
    #             "components": [{
    #                 "type": "body",
    #                 "parameters": [
    #                     {"type": "text", "text": vehicle_number},
    #                     {"type": "text", "text": final_message},
    #                 ]
    #             }]
    #         }
    #     }
    # )
    # response.raise_for_status()
    # return response.json()

    return {
        "status": "success",
        "message": f"WhatsApp sent to {owner_phone} (mock)",
    }
