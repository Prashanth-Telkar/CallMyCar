import logging

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# Persistent session with 1 retry on failures
_session = requests.Session()
_retry = Retry(total=1, backoff_factor=0.5, status_forcelist=[500, 502, 503, 504])
_session.mount("https://", HTTPAdapter(max_retries=_retry))

EXOTEL_URL = (
    f"https://api.exotel.com/v1/Accounts/{settings.EXOTEL_SID}/Calls/connect.json"
)


def connect_call(owner_phone: str, caller_phone: str) -> dict:
    """
    Initiate a masked call via Exotel between caller and vehicle owner.

    - From: caller's phone number (the scanner)
    - To: vehicle owner's phone number
    - CallerId: Exotel virtual number (masks both parties)
    """
    payload = {
        "From": caller_phone,
        "To": owner_phone,
        "CallerId": settings.EXOTEL_VIRTUAL_NUMBER,
    }

    logger.info(
        "Exotel connect_call: From=%s, To=%s, CallerId=%s",
        caller_phone,
        owner_phone,
        settings.EXOTEL_VIRTUAL_NUMBER,
    )

    try:
        response = _session.post(
            EXOTEL_URL,
            auth=(settings.EXOTEL_API_KEY, settings.EXOTEL_API_TOKEN),
            data=payload,
            timeout=10,
        )

        logger.info("Exotel response: status=%d, body=%s", response.status_code, response.text)

        response.raise_for_status()
        data = response.json()

        # Extract call SID from Exotel response
        call_data = data.get("Call", {})
        call_sid = call_data.get("Sid", "")

        return {
            "status": "success",
            "call_id": call_sid,
            "details": call_data,
        }

    except requests.exceptions.HTTPError as e:
        logger.error("Exotel HTTP error: %s — %s", e, e.response.text if e.response else "")
        raise RuntimeError(f"Exotel API error: {e.response.status_code}") from e
    except requests.exceptions.ConnectionError as e:
        logger.error("Exotel connection error: %s", e)
        raise RuntimeError("Could not reach Exotel API") from e
    except requests.exceptions.Timeout:
        logger.error("Exotel request timed out")
        raise RuntimeError("Exotel API timed out")
    except Exception as e:
        logger.error("Exotel unexpected error: %s", e)
        raise RuntimeError(f"Exotel call failed: {e}") from e
