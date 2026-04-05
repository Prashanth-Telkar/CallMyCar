"""
Bulk generate QR code IDs and insert them into the database.

Usage:
    python -m scripts.generate_qr_codes --count 1000
"""
import argparse
import uuid
import logging

from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.core.config import get_settings
from app.models.user import User  # noqa: F401
from app.models.vehicle import Vehicle  # noqa: F401
from app.models.qr_code import QRCode

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = get_settings()


def generate_qr_codes(count: int) -> list[str]:
    """Generate `count` unique QR code IDs and store them in the DB."""
    db: Session = SessionLocal()
    qr_ids: list[str] = []

    try:
        for i in range(count):
            qr_code_id = f"CMC-{uuid.uuid4().hex[:10].upper()}"
            qr = QRCode(qr_code_id=qr_code_id, is_active=False)
            db.add(qr)
            qr_ids.append(qr_code_id)

            if (i + 1) % 100 == 0:
                db.flush()
                logger.info("Generated %d / %d QR codes", i + 1, count)

        db.commit()
        logger.info("Successfully generated %d QR codes", count)
    except Exception:
        db.rollback()
        logger.exception("Failed to generate QR codes")
        raise
    finally:
        db.close()

    return qr_ids


def print_qr_urls(qr_ids: list[str]) -> None:
    """Print QR URLs for all generated IDs."""
    base = settings.BASE_URL.rstrip("/")
    for qr_id in qr_ids:
        print(f"{base}/v/{qr_id}")


def main():
    parser = argparse.ArgumentParser(description="Bulk generate QR code IDs")
    parser.add_argument("--count", type=int, default=1000, help="Number of QR codes to generate")
    parser.add_argument("--print-urls", action="store_true", help="Print QR URLs after generation")
    args = parser.parse_args()

    qr_ids = generate_qr_codes(args.count)

    if args.print_urls:
        print_qr_urls(qr_ids)
    else:
        logger.info("Use --print-urls to print all QR URLs")
        # Print first 5 as sample
        base = settings.BASE_URL.rstrip("/")
        for qr_id in qr_ids[:5]:
            print(f"  {base}/v/{qr_id}")
        if len(qr_ids) > 5:
            print(f"  ... and {len(qr_ids) - 5} more")


if __name__ == "__main__":
    main()
