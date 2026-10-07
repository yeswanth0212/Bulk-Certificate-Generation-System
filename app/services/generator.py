import io
import os
import math
import qrcode
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from app.config import settings

def generate_qr_code(verification_url: str) -> Image.Image:
    """Generates a high-contrast QR code image encoding the verification URL."""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=5,
        border=2,
    )
    qr.add_data(verification_url)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="#0B132B", back_color="#FFFFFF").convert("RGBA")
    return qr_img

def draw_corner_filigree(draw: ImageDraw.ImageDraw, x: int, y: int, flip_x: bool, flip_y: bool, color: tuple):
    """Draws an intricate metallic corner ornament filigree."""
    sx = -1 if flip_x else 1
    sy = -1 if flip_y else 1
    
    # Outer L-bracket lines
    draw.line([(x, y), (x + 80 * sx, y)], fill=color, width=4)
    draw.line([(x, y), (x, y + 80 * sy)], fill=color, width=4)
    
    # Inner parallel L-bracket
    draw.line([(x + 12 * sx, y + 12 * sy), (x + 70 * sx, y + 12 * sy)], fill=color, width=2)
    draw.line([(x + 12 * sx, y + 12 * sy), (x + 12 * sx, y + 70 * sy)], fill=color, width=2)
    
    # Corner Diamond
    dx, dy = x + 30 * sx, y + 30 * sy
    draw.polygon([
        (dx, dy - 15 * sy),
        (dx + 15 * sx, dy),
        (dx, dy + 15 * sy),
        (dx - 15 * sx, dy)
    ], fill=color)

def draw_star(draw: ImageDraw.ImageDraw, cx: int, cy: int, r_out: int, r_in: int, color: tuple):
    """Draws a 5-pointed star."""
    points = []
    for i in range(10):
        r = r_out if i % 2 == 0 else r_in
        angle = i * math.pi / 5 - math.pi / 2
        points.append((cx + int(r * math.cos(angle)), cy + int(r * math.sin(angle))))
    draw.polygon(points, fill=color)

def draw_diamond(draw: ImageDraw.ImageDraw, cx: int, cy: int, size: int, color: tuple):
    """Draws a diamond symbol."""
    draw.polygon([
        (cx, cy - size),
        (cx + size, cy),
        (cx, cy + size),
        (cx - size, cy)
    ], fill=color)

def draw_gold_emblem(image: Image.Image, center_x: int, center_y: int):
    """Draws an ultra-premium metallic gold medallion seal with flowing silk ribbons."""
    draw = ImageDraw.Draw(image)
    
    GOLD = (212, 160, 23)
    DARK_GOLD = (160, 110, 15)
    LIGHT_GOLD = (248, 222, 126)
    NAVY = (11, 19, 43)
    CRIMSON = (150, 25, 35)

    # 1. Dual Flowing Silk Ribbons at bottom
    # Left Ribbon
    draw.polygon([
        (center_x - 30, center_y + 40),
        (center_x - 70, center_y + 160),
        (center_x - 45, center_y + 150),
        (center_x - 20, center_y + 165),
        (center_x - 10, center_y + 40)
    ], fill=CRIMSON, outline=DARK_GOLD)

    # Right Ribbon
    draw.polygon([
        (center_x + 10, center_y + 40),
        (center_x + 20, center_y + 165),
        (center_x + 45, center_y + 150),
        (center_x + 70, center_y + 160),
        (center_x + 30, center_y + 40)
    ], fill=CRIMSON, outline=DARK_GOLD)

    # 2. Outer Starburst Sunburst Rays (24 points)
    outer_r = 75
    inner_r = 65
    points = []
    num_pts = 24
    for i in range(num_pts * 2):
        r = outer_r if i % 2 == 0 else inner_r
        angle = i * (math.pi / num_pts)
        px = center_x + int(r * math.cos(angle))
        py = center_y + int(r * math.sin(angle))
        points.append((px, py))
    draw.polygon(points, fill=GOLD, outline=DARK_GOLD)

    # 3. Concentric Gold Rings
    draw.ellipse([center_x - 62, center_y - 62, center_x + 62, center_y + 62], fill=LIGHT_GOLD, outline=DARK_GOLD, width=2)
    draw.ellipse([center_x - 54, center_y - 54, center_x + 54, center_y + 54], fill=GOLD, outline=DARK_GOLD, width=3)
    
    # 4. Deep Navy Center Core
    draw.ellipse([center_x - 44, center_y - 44, center_x + 44, center_y + 44], fill=NAVY, outline=LIGHT_GOLD, width=2)

    # 5. Inner Gold Star & Text Ring
    draw_star(draw, center_x, center_y - 8, r_out=18, r_in=8, color=LIGHT_GOLD)
    
    def load_font(size):
        for f in ["arialbd.ttf", "timesbd.ttf", "DejaVuSans-Bold.ttf"]:
            try: return ImageFont.truetype(f, size)
            except IOError: continue
        return ImageFont.load_default()

    draw.text((center_x, center_y + 20), "OFFICIAL", font=load_font(12), fill=LIGHT_GOLD, anchor="mm")

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
    Renders an ultra-premium executive diploma certificate with high-end typography,
    golden corner filigrees, background guilloché patterns, and embedded verification QR.
    """
    width, height = 2400, 1700
    
    # 1. Base Luxury Cream Canvas with Subtle Textured Shading
    image = Image.new("RGBA", (width, height), "#FAF7F2")
    draw = ImageDraw.Draw(image)

    # Colors Palette
    NAVY = (11, 19, 43)        # Deep Royal Navy
    GOLD = (200, 145, 20)       # Polished Gold
    DARK_GOLD = (150, 100, 10)  # Rich Antique Gold
    SLATE = (71, 85, 105)      # Slate Gray
    LIGHT_GOLD = (252, 246, 222)# Cream Gold
    ACCENT_RED = (140, 20, 30)

    # 2. Draw Subtle Guilloché Background Lattice Lines (Watermark Effect)
    grid_spacing = 80
    for i in range(-height, width + height, grid_spacing):
        draw.line([(i, 0), (i + height, height)], fill=(238, 232, 220), width=1)
        draw.line([(i, height), (i + height, 0)], fill=(238, 232, 220), width=1)

    # 3. Quadruple Ornamental Borders
    draw.rectangle([45, 45, width - 45, height - 45], outline=NAVY, width=10)
    draw.rectangle([62, 62, width - 62, height - 62], outline=GOLD, width=3)
    draw.rectangle([74, 74, width - 74, height - 74], outline=DARK_GOLD, width=8)
    draw.rectangle([92, 92, width - 92, height - 92], outline=NAVY, width=2)
    draw.rectangle([104, 104, width - 104, height - 104], outline=LIGHT_GOLD, width=4)

    # 4. Corner Filigree Ornaments
    draw_corner_filigree(draw, 115, 115, flip_x=False, flip_y=False, color=DARK_GOLD)
    draw_corner_filigree(draw, width - 115, 115, flip_x=True, flip_y=False, color=DARK_GOLD)
    draw_corner_filigree(draw, 115, height - 115, flip_x=False, flip_y=True, color=DARK_GOLD)
    draw_corner_filigree(draw, width - 115, height - 115, flip_x=True, flip_y=True, color=DARK_GOLD)

    # 5. Dynamic Fonts Loader
    def get_font(size: int, is_bold: bool = False, is_script: bool = False):
        font_names = []
        if is_script:
            font_names = [
                "BrushScript.ttf", "SegoeScript.ttf", "LucidaHandwriting.ttf",
                "timesi.ttf", "georgiai.ttf", "ariali.ttf", "DejaVuSans-Oblique.ttf"
            ]
        elif is_bold:
            font_names = ["timesbd.ttf", "georgiab.ttf", "arialbd.ttf", "DejaVuSans-Bold.ttf"]
        else:
            font_names = ["times.ttf", "georgia.ttf", "arial.ttf", "DejaVuSans.ttf"]
        
        for fn in font_names:
            try:
                return ImageFont.truetype(fn, size)
            except IOError:
                continue
        return ImageFont.load_default()

    font_issuer = get_font(44, is_bold=True)
    font_header = get_font(72, is_bold=True)
    font_sub = get_font(34, is_bold=False)
    font_name = get_font(88, is_bold=True)
    font_title = get_font(54, is_bold=True)
    font_custom = get_font(36, is_bold=False)
    font_meta = get_font(28, is_bold=False)
    font_sig_name = get_font(30, is_bold=True)
    font_script = get_font(52, is_script=True)

    # 6. Render Gold Medallion Emblem at Top Center
    draw_gold_emblem(image, width // 2, 215)

    y_cursor = 370

    # Issuer Name flanked by vector diamonds
    issuer_text = issuer_name.upper()
    draw.text((width // 2, y_cursor), issuer_text, font=font_issuer, fill=GOLD, anchor="mm")
    
    # Calculate issuer text bounds for vector diamond accents
    iss_bbox = draw.textbbox((width // 2, y_cursor), issuer_text, font=font_issuer, anchor="mm")
    iss_w = (iss_bbox[2] - iss_bbox[0]) // 2 + 40
    draw_diamond(draw, width // 2 - iss_w, y_cursor, size=10, color=GOLD)
    draw_diamond(draw, width // 2 + iss_w, y_cursor, size=10, color=GOLD)

    y_cursor += 105

    # Main Certificate Title
    draw.text((width // 2, y_cursor), "CERTIFICATE OF ACHIEVEMENT", font=font_header, fill=NAVY, anchor="mm")
    y_cursor += 85

    # Ornate Center Divider Line with diamonds
    draw.line([(width // 2 - 320, y_cursor), (width // 2 + 320, y_cursor)], fill=GOLD, width=4)
    draw_diamond(draw, width // 2 - 15, y_cursor, size=10, color=DARK_GOLD)
    draw_diamond(draw, width // 2 + 15, y_cursor, size=10, color=DARK_GOLD)
    y_cursor += 75

    # Presentation Context
    draw.text((width // 2, y_cursor), "THIS IS TO CERTIFY THAT", font=font_sub, fill=SLATE, anchor="mm")
    y_cursor += 125

    # Recipient Name with Decorative Soft Backdrop Banner
    name_bbox = draw.textbbox((width // 2, y_cursor), recipient_name, font=font_name, anchor="mm")
    box_w = (name_bbox[2] - name_bbox[0]) + 120
    box_h = 130
    banner_rect = [width // 2 - box_w // 2, y_cursor - box_h // 2, width // 2 + box_w // 2, y_cursor + box_h // 2]
    draw.rectangle(banner_rect, fill=(255, 253, 245), outline=LIGHT_GOLD, width=2)
    draw.rectangle([banner_rect[0] - 4, banner_rect[1] - 4, banner_rect[2] + 4, banner_rect[3] + 4], outline=GOLD, width=1)
    
    draw.text((width // 2, y_cursor), recipient_name, font=font_name, fill=NAVY, anchor="mm")
    y_cursor += 140

    # Recognition Detail Line
    draw.text((width // 2, y_cursor), "has successfully completed all prescribed requirements and masterclass modules for", font=font_sub, fill=SLATE, anchor="mm")
    y_cursor += 90

    # Course Title
    draw.text((width // 2, y_cursor), course_title, font=font_title, fill=DARK_GOLD, anchor="mm")
    y_cursor += 80

    # Custom Note / Grade Text (if present)
    if custom_text:
        draw.text((width // 2, y_cursor), f"Special Distinction: {custom_text}", font=font_custom, fill=NAVY, anchor="mm")
        y_cursor += 70

    # 7. Bottom Section: Left Metadata, Center Signature, Right Verification QR
    bottom_y = height - 260

    # Left Column: Date & ID Box
    draw.text((180, bottom_y), f"Date of Issue: {issue_date}", font=font_meta, fill=SLATE)
    draw.text((180, bottom_y + 45), f"Certificate ID: {cert_id}", font=font_meta, fill=NAVY)
    draw.text((180, bottom_y + 85), "Security Status: [ VERIFIED RECORD ]", font=get_font(22, is_bold=True), fill=ACCENT_RED)

    # Center Column: Signature Line & Cursive Script
    sig_x = width // 2
    sig_display_name = signatory_name or "Dr. Alex Vance"
    sig_display_title = signatory_title or "Director of Certification"

    # Cursive signature above line
    draw.text((sig_x, bottom_y - 15), sig_display_name, font=font_script, fill=NAVY, anchor="mm")
    
    # Signature underline with ornamental end loops
    draw.line([(sig_x - 200, bottom_y + 35), (sig_x + 200, bottom_y + 35)], fill=NAVY, width=3)
    draw.ellipse([sig_x - 206, bottom_y + 31, sig_x - 194, bottom_y + 39], fill=GOLD)
    draw.ellipse([sig_x + 194, bottom_y + 31, sig_x + 206, bottom_y + 39], fill=GOLD)

    # Signatory details
    draw.text((sig_x, bottom_y + 65), sig_display_name, font=font_sig_name, fill=NAVY, anchor="mm")
    draw.text((sig_x, bottom_y + 100), sig_display_title, font=font_meta, fill=SLATE, anchor="mm")

    # Right Column: Framed Verification QR Code
    verify_url = f"{settings.BASE_URL}/api/v1/certificates/{cert_id}/verify"
    qr_img = generate_qr_code(verify_url)
    qr_w, qr_h = qr_img.size
    qr_x, qr_y = width - 360, bottom_y - 45
    
    # Frame card for QR code
    draw.rectangle([qr_x - 12, qr_y - 12, qr_x + qr_w + 12, qr_y + qr_h + 35], fill=(255, 255, 255), outline=GOLD, width=2)
    image.paste(qr_img, (qr_x, qr_y), qr_img)
    draw.text((qr_x + qr_w // 2, qr_y + qr_h + 12), "SCAN TO VERIFY", font=get_font(18, is_bold=True), fill=NAVY, anchor="mm")

    # 8. Save File (PDF or PNG)
    output_filename = f"{cert_id}.{output_format.lower()}"
    output_path = settings.OUTPUT_DIR / output_filename

    rgb_image = image.convert("RGB")
    if output_format.lower() == "pdf":
        rgb_image.save(output_path, "PDF", resolution=150.0)
    else:
        rgb_image.save(output_path, "PNG")

    return output_path
