import io
import os
import qrcode
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from app.config import settings

def generate_qr_code(verification_url: str) -> Image.Image:
    """Generates a QR code image encoding the verification URL."""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=4,
        border=2,
    )
    qr.add_data(verification_url)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="#0F172A", back_color="#FFFFFF").convert("RGBA")
    return qr_img

def render_certificate(
    cert_id: str,
    recipient_name: str,
    course_title: str,
    issuer_name: str,
    issue_date: str,
    custom_text: str = None,
    signatory_name: str = "Dr. Alex Vance",
    signatory_title: str = "Director of Certification",
    output_format: str = "pdf"
) -> Path:
    """
    Renders a high-resolution certificate for a recipient and saves it to output storage.
    Supports both PDF and PNG output formats.
    """
    # 1. Canvas Dimensions (2000 x 1414 - HD Landscape Certificate)
    width, height = 2000, 1414
    image = Image.new("RGBA", (width, height), "#FDFBF7")
    draw = ImageDraw.Draw(image)

    # Colors
    NAVY = (15, 23, 42)
    GOLD = (180, 120, 20)
    DARK_GOLD = (130, 85, 10)
    SLATE = (71, 85, 105)
    LIGHT_GOLD = (245, 230, 190)

    # 2. Draw Decorative Borders
    # Outer Border
    draw.rectangle([40, 40, width - 40, height - 40], outline=NAVY, width=8)
    # Inner Gold Border
    draw.rectangle([55, 55, width - 55, height - 55], outline=GOLD, width=3)
    # Corner Accents
    corner_size = 30
    corners = [
        (40, 40), (width - 40, 40),
        (40, height - 40), (width - 40, height - 40)
    ]
    for cx, cy in corners:
        draw.rectangle([cx - corner_size, cy - corner_size, cx + corner_size, cy + corner_size], fill=DARK_GOLD)

    # 3. Font Selection with standard fallback
    def get_font(size: int, is_bold: bool = False, is_script: bool = False):
        font_names = []
        if is_script:
            font_names = [
                "BrushScript.ttf", "SegoeScript.ttf", "LucidaHandwriting.ttf",
                "timesi.ttf", "georgiai.ttf", "ariali.ttf", "DejaVuSans-Oblique.ttf"
            ]
        elif is_bold:
            font_names = ["arialbd.ttf", "timesbd.ttf", "georgiab.ttf", "DejaVuSans-Bold.ttf"]
        else:
            font_names = ["arial.ttf", "times.ttf", "georgia.ttf", "DejaVuSans.ttf"]
        
        for fn in font_names:
            try:
                return ImageFont.truetype(fn, size)
            except IOError:
                continue
        return ImageFont.load_default()

    font_issuer = get_font(42, is_bold=True)
    font_header = get_font(60, is_bold=True)
    font_sub = get_font(32, is_bold=False)
    font_name = get_font(72, is_bold=True)
    font_title = get_font(48, is_bold=True)
    font_custom = get_font(32, is_bold=False)
    font_meta = get_font(26, is_bold=False)
    font_sig_name = get_font(26, is_bold=True)
    font_script = get_font(46, is_script=True)

    # 4. Content Assembly
    y_cursor = 160

    # Top Medallion / Emblem representation
    medallion_x = width // 2
    draw.ellipse([medallion_x - 45, y_cursor, medallion_x + 45, y_cursor + 90], fill=GOLD, outline=NAVY, width=3)
    draw.ellipse([medallion_x - 35, y_cursor + 10, medallion_x + 35, y_cursor + 80], fill=LIGHT_GOLD)
    draw.text((medallion_x, y_cursor + 45), "★", font=get_font(36, True), fill=NAVY, anchor="mm")
    y_cursor += 130

    # Issuer Name
    draw.text((width // 2, y_cursor), issuer_name.upper(), font=font_issuer, fill=GOLD, anchor="mm")
    y_cursor += 90

    # Certificate Header Title
    draw.text((width // 2, y_cursor), "CERTIFICATE OF ACHIEVEMENT", font=font_header, fill=NAVY, anchor="mm")
    y_cursor += 75

    # Horizontal Divider Line
    draw.line([(width // 2 - 250, y_cursor), (width // 2 + 250, y_cursor)], fill=GOLD, width=3)
    y_cursor += 65

    # Presentation Text
    draw.text((width // 2, y_cursor), "THIS CERTIFICATE IS PROUDLY PRESENTED TO", font=font_sub, fill=SLATE, anchor="mm")
    y_cursor += 100

    # Recipient Name
    draw.text((width // 2, y_cursor), recipient_name, font=font_name, fill=NAVY, anchor="mm")
    # Decorative underline for name
    name_bbox = draw.textbbox((width // 2, y_cursor), recipient_name, font=font_name, anchor="mm")
    name_width = name_bbox[2] - name_bbox[0]
    draw.line([(width // 2 - name_width // 2 - 20, y_cursor + 50), (width // 2 + name_width // 2 + 20, y_cursor + 50)], fill=DARK_GOLD, width=2)
    y_cursor += 120

    # Recognition Context
    draw.text((width // 2, y_cursor), "for successful completion and mastery of", font=font_sub, fill=SLATE, anchor="mm")
    y_cursor += 75

    # Course / Event Title
    draw.text((width // 2, y_cursor), course_title, font=font_title, fill=NAVY, anchor="mm")
    y_cursor += 70

    # Custom Text (if provided)
    if custom_text:
        draw.text((width // 2, y_cursor), f"({custom_text})", font=font_custom, fill=GOLD, anchor="mm")
        y_cursor += 60

    # 5. Bottom Section: Date, Signature Line, and QR Code
    bottom_y = height - 230

    # Left: Date & Certificate ID
    draw.text((150, bottom_y), f"Date of Issue: {issue_date}", font=font_meta, fill=SLATE)
    draw.text((150, bottom_y + 40), f"Certificate ID: {cert_id}", font=font_meta, fill=SLATE)

    # Center: Cursive Signature & Authorized Signature Line
    sig_x = width // 2

    # Render cursive handwriting signature above line
    sig_display_name = signatory_name or "Dr. Alex Vance"
    sig_display_title = signatory_title or "Director of Certification"
    draw.text((sig_x, bottom_y - 15), sig_display_name, font=font_script, fill=NAVY, anchor="mm")

    # Signature Line
    draw.line([(sig_x - 170, bottom_y + 30), (sig_x + 170, bottom_y + 30)], fill=NAVY, width=2)
    
    # Signatory Name & Title below line
    draw.text((sig_x, bottom_y + 55), sig_display_name, font=font_sig_name, fill=NAVY, anchor="mm")
    draw.text((sig_x, bottom_y + 85), sig_display_title, font=font_meta, fill=SLATE, anchor="mm")

    # Right: Verification QR Code
    verify_url = f"{settings.BASE_URL}/api/v1/certificates/{cert_id}/verify"
    qr_img = generate_qr_code(verify_url)
    qr_w, qr_h = qr_img.size
    qr_pos = (width - 250, bottom_y - 20)
    image.paste(qr_img, qr_pos, qr_img)
    draw.text((width - 250 + qr_w // 2, bottom_y + qr_h - 10), "Scan to Verify", font=get_font(20), fill=SLATE, anchor="mm")

    # 6. Save File (PDF or PNG)
    output_filename = f"{cert_id}.{output_format.lower()}"
    output_path = settings.OUTPUT_DIR / output_filename

    rgb_image = image.convert("RGB")
    if output_format.lower() == "pdf":
        rgb_image.save(output_path, "PDF", resolution=100.0)
    else:
        rgb_image.save(output_path, "PNG")

    return output_path
