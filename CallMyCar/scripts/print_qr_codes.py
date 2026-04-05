"""
Generate printable QR code PNG images for all QR codes in the database.

Usage:
    python -m scripts.print_qr_codes
    python -m scripts.print_qr_codes --base-url https://yourdomain.com
    python -m scripts.print_qr_codes --output-dir my_qr_images

Each PNG includes the QR code + the code ID label below it.
"""
import argparse
import logging
import os

import qrcode
from PIL import Image, ImageDraw, ImageFont

from app.core.database import SessionLocal
from app.core.config import get_settings
from app.models.user import User  # noqa: F401
from app.models.vehicle import Vehicle  # noqa: F401
from app.models.qr_code import QRCode

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = get_settings()


def fetch_all_qr_ids() -> list[str]:
    """Fetch all QR code IDs from the database."""
    db = SessionLocal()
    try:
        codes = db.query(QRCode.qr_code_id).order_by(QRCode.qr_code_id).all()
        return [c[0] for c in codes]
    finally:
        db.close()


def generate_qr_image(qr_code_id: str, base_url: str, output_dir: str) -> str:
    """Generate a single QR code PNG with a label underneath."""
    url = f"{base_url}/v/{qr_code_id}"

    # Generate QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=12,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white").convert("RGB")

    qr_w, qr_h = qr_img.size

    # Build final image with label
    label_height = 60
    padding = 20
    total_w = qr_w + padding * 2
    total_h = qr_h + label_height + padding * 2

    canvas = Image.new("RGB", (total_w, total_h), "white")
    canvas.paste(qr_img, (padding, padding))

    # Draw label text
    draw = ImageDraw.Draw(canvas)
    try:
        font = ImageFont.truetype("arial.ttf", 22)
        font_small = ImageFont.truetype("arial.ttf", 14)
    except OSError:
        font = ImageFont.load_default()
        font_small = font

    # QR code ID
    bbox = draw.textbbox((0, 0), qr_code_id, font=font)
    text_w = bbox[2] - bbox[0]
    draw.text(
        ((total_w - text_w) / 2, qr_h + padding + 5),
        qr_code_id,
        fill="black",
        font=font,
    )

    # "CallMyCar" branding
    brand = "CallMyCar"
    bbox2 = draw.textbbox((0, 0), brand, font=font_small)
    brand_w = bbox2[2] - bbox2[0]
    draw.text(
        ((total_w - brand_w) / 2, qr_h + padding + 32),
        brand,
        fill="#6366f1",
        font=font_small,
    )

    # Save
    filename = f"{qr_code_id}.png"
    filepath = os.path.join(output_dir, filename)
    canvas.save(filepath, "PNG")
    return filepath


def main():
    parser = argparse.ArgumentParser(description="Generate printable QR code images")
    parser.add_argument(
        "--base-url",
        type=str,
        default=settings.BASE_URL.rstrip("/"),
        help="Base URL for QR links (default: from .env)",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="qr_images",
        help="Output directory for PNG files (default: qr_images)",
    )
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)

    qr_ids = fetch_all_qr_ids()
    if not qr_ids:
        logger.warning("No QR codes found in the database.")
        return

    logger.info("Generating %d QR code images...", len(qr_ids))

    for qr_id in qr_ids:
        path = generate_qr_image(qr_id, args.base_url, args.output_dir)
        print(f"  ✓ {path}")

    logger.info("Done! %d images saved to %s/", len(qr_ids), args.output_dir)


if __name__ == "__main__":
    main()
