from PIL import Image, ImageDraw, ImageFont

W, H = 420, 700
BG = (15, 23, 36)
BOT_BUBBLE = (33, 47, 65)
BTN = (38, 89, 138)
BTN_TEXT = (255, 255, 255)
TEXT = (230, 230, 230)
HEADER = (24, 35, 51)

def font(size, bold=False):
    paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for p in paths:
        try:
            return ImageFont.truetype(p, size)
        except Exception:
            continue
    return ImageFont.load_default()

def rounded(draw, box, radius, fill):
    draw.rounded_rectangle(box, radius=radius, fill=fill)

def base_canvas(title):
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 60], fill=HEADER)
    d.ellipse([14, 12, 50, 48], fill=(80, 130, 180))
    d.text((60, 18), title, font=font(18, True), fill=TEXT)
    d.text((60, 38), "online", font=font(12), fill=(130, 200, 130))
    return img, d

def bot_bubble(d, y, lines, width=300):
    pad = 14
    line_h = 20
    box_h = pad * 2 + line_h * len(lines)
    rounded(d, [14, y, 14 + width, y + box_h], 14, BOT_BUBBLE)
    for i, line in enumerate(lines):
        d.text((14 + pad, y + pad + i * line_h), line, font=font(14), fill=TEXT)
    return y + box_h + 10

def buttons(d, y, labels, width=300):
    pad_y = 8
    for label in labels:
        h = 36
        rounded(d, [14, y, 14 + width, y + h], 10, BTN)
        bbox = d.textbbox((0, 0), label, font=font(14))
        tw = bbox[2] - bbox[0]
        d.text((14 + (width - tw) / 2, y + 9), label, font=font(14), fill=BTN_TEXT)
        y += h + pad_y
    return y

# 1. Service selection
img, d = base_canvas("Booking Bot")
y = 80
y = bot_bubble(d, y, ["👋 Welcome! Let's book", "your appointment.", "", "What service would you like?"])
y = buttons(d, y, ["Haircut — 30 min", "Massage — 60 min", "Consultation — 15 min"])
img.save("/home/claude/telegram-booking-bot/screenshots/1_choose_service.png")

# 2. Date selection
img, d = base_canvas("Booking Bot")
y = 80
y = bot_bubble(d, y, ["Service: Haircut — 30 min", "", "Choose a date:"])
y = buttons(d, y, ["Mon 30 Jun", "Tue 01 Jul", "Wed 02 Jul", "Thu 03 Jul", "Fri 04 Jul"])
img.save("/home/claude/telegram-booking-bot/screenshots/2_choose_date.png")

# 3. Time selection
img, d = base_canvas("Booking Bot")
y = 80
y = bot_bubble(d, y, ["Date: 2026-07-01", "", "Available times:"])
y = buttons(d, y, ["10:00", "11:00", "14:00", "15:00", "17:00"])
img.save("/home/claude/telegram-booking-bot/screenshots/3_choose_time.png")

# 4. Confirmation
img, d = base_canvas("Booking Bot")
y = 80
y = bot_bubble(d, y, ["Please confirm:", "", "🛎 Haircut — 30 min", "📅 2026-07-01", "⏰ 11:00"])
y = buttons(d, y, ["✅ Confirm", "❌ Cancel"])
img.save("/home/claude/telegram-booking-bot/screenshots/4_confirm.png")

# 5. Final confirmation message
img, d = base_canvas("Booking Bot")
y = 80
y = bot_bubble(d, y, [
    "✅ Booking confirmed!", "",
    "Reference: #7",
    "🛎 Haircut — 30 min",
    "📅 2026-07-01",
    "⏰ 11:00", "",
    "See your bookings any time", "with /my_bookings.",
])
img.save("/home/claude/telegram-booking-bot/screenshots/5_booking_confirmed.png")

# 6. My bookings list with cancel button
img, d = base_canvas("Booking Bot")
y = 80
y = bot_bubble(d, y, ["#7 — Haircut — 30 min", "📅 2026-07-01  ⏰ 11:00"])
y = buttons(d, y, ["Cancel this booking"])
y += 10
y = bot_bubble(d, y, ["#9 — Massage — 60 min", "📅 2026-07-03  ⏰ 15:00"])
y = buttons(d, y, ["Cancel this booking"])
img.save("/home/claude/telegram-booking-bot/screenshots/6_my_bookings.png")

print("done")
