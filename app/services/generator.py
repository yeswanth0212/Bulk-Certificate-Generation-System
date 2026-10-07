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
        border=1,
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

    # 1. Dual Flowing Silk Ribbons at bottom (Ending cleanly at center_y + 125)
    # Left Ribbon
    draw.polygon([
        (center_x - 25, center_y + 35),
        (center_x - 55, center_y + 125),
        (center_x - 38, center_y + 115),
        (center_x - 20, center_y + 128),
        (center_x - 8, center_y + 35)
    ], fill=CRIMSON, outline=DARK_GOLD)

    # Right Ribbon
    draw.polygon([
        (center_x + 8, center_y + 35),
        (center_x + 20, center_y + 128),
        (center_x + 38, center_y + 115),
        (center_x + 55, center_y + 125),
        (center_x + 25, center_y + 35)
    ], fill=CRIMSON, outline=DARK_GOLD)

    # 2. Outer Starburst Sunburst Rays (24 points)
    outer_r = 65
    inner_r = 55
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
    draw.ellipse([center_x - 52, center_y - 52, center_x + 52, center_y + 52], fill=LIGHT_GOLD, outline=DARK_GOLD, width=2)
    draw.ellipse([center_x - 45, center_y - 45, center_x + 45, center_y + 45], fill=GOLD, outline=DARK_GOLD, width=2)
    
    # 4. Deep Navy Center Core
    draw.ellipse([center_x - 36, center_y - 36, center_x + 36, center_y + 36], fill=NAVY, outline=LIGHT_GOLD, width=2)

    # 5. Inner Gold Star & Text Ring
    draw_star(draw, center_x, center_y - 6, r_out=14, r_in=6, color=LIGHT_GOLD)
    
    def load_font(size):
        for f in ["arialbd.ttf", "timesbd.ttf", "DejaVuSans-Bold.ttf"]:
            try: return ImageFont.truetype(f, size)
            except IOError: continue
        return ImageFont.load_default()

    draw.text((center_x, center_y + 16), "OFFICIAL", font=load_font(10), fill=LIGHT_GOLD, anchor="mm")

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
    Renders an ultra-premium executive diploma certificate with mathematically perfect alignment,
    golden corner filigrees, background guilloché patterns, and embedded verification QR.
    """
    width, height = 2400, 1700
    
    # 1. Base Luxury Cream Canvas
    image = Image.new("RGBA", (width, height), "#FAF7F2")
    draw = ImageDraw.Draw(image)

    # Color Palette
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

    font_issuer = get_font(42, is_bold=True)
    font_header = get_font(68, is_bold=True)
    font_sub = get_font(32, is_bold=False)
    font_name = get_font(84, is_bold=True)
    font_title = get_font(52, is_bold=True)
    font_custom = get_font(34, is_bold=False)
    font_meta = get_font(26, is_bold=False)
    font_sig_name = get_font(28, is_bold=True)
    font_script = get_font(50, is_script=True)

    # 6. Render Gold Medallion Emblem at Top Center (Center Y = 200, Ribbon ends at Y = 328)
    draw_gold_emblem(image, width // 2, 200)

    # 7. Main Vertical Content Layout (With precise spacing!)
    
    # Issuer Name (Y = 385, no overlap with medallion ribbon)
    issuer_text = issuer_name.upper()
    draw.text((width // 2, 385), issuer_text, font=font_issuer, fill=GOLD, anchor="mm")
    
    iss_bbox = draw.textbbox((width // 2, 385), issuer_text, font=font_issuer, anchor="mm")
    iss_w = (iss_bbox[2] - iss_bbox[0]) // 2 + 40
    draw_diamond(draw, width // 2 - iss_w, 385, size=10, color=GOLD)
    draw_diamond(draw, width // 2 + iss_w, 385, size=10, color=GOLD)

    # Certificate Title (Y = 475)
    draw.text((width // 2, 475), "CERTIFICATE OF ACHIEVEMENT", font=font_header, fill=NAVY, anchor="mm")

    # Center Divider Line (Y = 545)
    draw.line([(width // 2 - 320, 545), (width // 2 + 320, 545)], fill=GOLD, width=4)
    draw_diamond(draw, width // 2 - 15, 545, size=10, color=DARK_GOLD)
    draw_diamond(draw, width // 2 + 15, 545, size=10, color=DARK_GOLD)

    # Presentation Context (Y = 620)
    draw.text((width // 2, 620), "THIS IS TO CERTIFY THAT", font=font_sub, fill=SLATE, anchor="mm")

    # Recipient Name with Centered Banner Box (Y = 740)
    name_y = 740
    name_bbox = draw.textbbox((width // 2, name_y), recipient_name, font=font_name, anchor="mm")
    box_w = max((name_bbox[2] - name_bbox[0]) + 140, 600)
    box_h = 120
    banner_rect = [width // 2 - box_w // 2, name_y - box_h // 2, width // 2 + box_w // 2, name_y + box_h // 2]
    draw.rectangle(banner_rect, fill=(255, 253, 245), outline=LIGHT_GOLD, width=2)
    draw.rectangle([banner_rect[0] - 4, banner_rect[1] - 4, banner_rect[2] + 4, banner_rect[3] + 4], outline=GOLD, width=1)
    
    draw.text((width // 2, name_y), recipient_name, font=font_name, fill=NAVY, anchor="mm")

    # Completion Description (Y = 875)
    draw.text((width // 2, 875), "has successfully completed all prescribed requirements and masterclass modules for", font=font_sub, fill=SLATE, anchor="mm")

    # Course Title (Y = 965)
    draw.text((width // 2, 965), course_title, font=font_title, fill=DARK_GOLD, anchor="mm")

    # Custom Note / Grade (Y = 1045)
    if custom_text:
        draw.text((width // 2, 1045), f"Special Distinction: {custom_text}", font=font_custom, fill=NAVY, anchor="mm")

    # 8. Bottom Footer Section (Aligned perfectly on Y = 1350 to Y = 1530)
    
    # Left Column: Date & Security Metadata
    left_x = 180
    draw.text((left_x, 1360), f"Date of Issue: {issue_date}", font=font_meta, fill=SLATE)
    draw.text((left_x, 1405), f"Certificate ID: {cert_id}", font=font_meta, fill=NAVY)
    draw.text((left_x, 1450), "Security Status: [ VERIFIED RECORD ]", font=get_font(22, is_bold=True), fill=ACCENT_RED)

    # Center Column: Signature Line & Details
    sig_x = width // 2
    sig_display_name = signatory_name or "Dr. Alex Vance"
    sig_display_title = signatory_title or "Director of Certification"

    # Cursive signature above line (Y = 1345)
    draw.text((sig_x, 1345), sig_display_name, font=font_script, fill=NAVY, anchor="mm")
    
    # Signature underline (Y = 1395)
    draw.line([(sig_x - 200, 1395), (sig_x + 200, 1395)], fill=NAVY, width=3)
    draw.ellipse([sig_x - 206, 1391, sig_x - 194, 1399], fill=GOLD)
    draw.ellipse([sig_x + 194, 1391, sig_x + 206, 1399], fill=GOLD)

    # Signatory details (Y = 1435 and 1470)
    draw.text((sig_x, 1435), sig_display_name, font=font_sig_name, fill=NAVY, anchor="mm")
    draw.text((sig_x, 1470), sig_display_title, font=font_meta, fill=SLATE, anchor="mm")

    # Right Column: QR Verification Card (Y = 1330 to 1530)
    verify_url = f"{settings.BASE_URL}/api/v1/certificates/{cert_id}/verify"
    qr_img = generate_qr_code(verify_url)
    qr_w, qr_h = qr_img.size
    qr_x, qr_y = width - 400, 1330
    
    # Frame card for QR code
    card_padding = 16
    draw.rectangle([qr_x - card_padding, qr_y - card_padding, qr_x + qr_w + card_padding, qr_y + qr_h + 40], fill=(255, 255, 255), outline=GOLD, width=2)
    image.paste(qr_img, (qr_x, qr_y), qr_img)
    draw.text((qr_x + qr_w // 2, qr_y + qr_h + 16), "SCAN TO VERIFY", font=get_font(18, is_bold=True), fill=NAVY, anchor="mm")

    # 9. Save File (PDF or PNG)
    output_filename = f"{cert_id}.{output_format.lower()}"
    output_path = settings.OUTPUT_DIR / output_filename

    rgb_image = image.convert("RGB")
    if output_format.lower() == "pdf":
        rgb_image.save(output_path, "PDF", resolution=150.0)
    else:
        rgb_image.save(output_path, "PNG")

    return output_path
