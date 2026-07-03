"""
Booking conversation flow:

/start or /book
  -> choose service        (inline buttons)
  -> choose date            (next 5 days, inline buttons)
  -> choose time slot       (filters out already-booked slots)
  -> confirm                (Yes / Cancel)
  -> booking saved to DB, confirmation message sent

/my_bookings  -> lists active bookings with a Cancel button per row
"""
from datetime import datetime, timedelta

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CallbackQueryHandler,
    CommandHandler,
)

from bot.config import AVAILABLE_SLOTS, SERVICES
from bot import database as db

CHOOSING_SERVICE, CHOOSING_DATE, CHOOSING_TIME, CONFIRMING = range(4)


def _date_options():
    today = datetime.now().date()
    return [today + timedelta(days=i) for i in range(5)]


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome! Let's book your appointment.\n\nWhat service would you like?",
    )
    return await show_services(update, context)


async def show_services(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton(label, callback_data=f"svc:{key}")]
        for key, label in SERVICES.items()
    ]
    target = update.message or update.callback_query.message
    await target.reply_text("Choose a service:", reply_markup=InlineKeyboardMarkup(keyboard))
    return CHOOSING_SERVICE


async def service_chosen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    service_key = query.data.split(":", 1)[1]
    context.user_data["service"] = service_key

    keyboard = [
        [InlineKeyboardButton(d.strftime("%a %d %b"), callback_data=f"date:{d.isoformat()}")]
        for d in _date_options()
    ]
    await query.edit_message_text(
        f"Service: {SERVICES[service_key]}\n\nChoose a date:",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )
    return CHOOSING_DATE


async def date_chosen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    slot_date = query.data.split(":", 1)[1]
    context.user_data["date"] = slot_date

    free_slots = [t for t in AVAILABLE_SLOTS if not db.is_slot_taken(slot_date, t)]
    if not free_slots:
        await query.edit_message_text("No free slots that day, sorry! Pick another date with /book.")
        return ConversationHandler.END

    keyboard = [
        [InlineKeyboardButton(t, callback_data=f"time:{t}")] for t in free_slots
    ]
    await query.edit_message_text(
        f"Date: {slot_date}\n\nAvailable times:",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )
    return CHOOSING_TIME


async def time_chosen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    slot_time = query.data.split(":", 1)[1]
    context.user_data["time"] = slot_time

    service = SERVICES[context.user_data["service"]]
    date = context.user_data["date"]
    keyboard = [
        [
            InlineKeyboardButton("✅ Confirm", callback_data="confirm:yes"),
            InlineKeyboardButton("❌ Cancel", callback_data="confirm:no"),
        ]
    ]
    await query.edit_message_text(
        f"Please confirm:\n\n🛎 {service}\n📅 {date}\n⏰ {slot_time}",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )
    return CONFIRMING


async def confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    choice = query.data.split(":", 1)[1]

    if choice == "no":
        await query.edit_message_text("Booking cancelled. Send /book to start again.")
        context.user_data.clear()
        return ConversationHandler.END

    user = query.from_user
    service_key = context.user_data["service"]
    slot_date = context.user_data["date"]
    slot_time = context.user_data["time"]

    if db.is_slot_taken(slot_date, slot_time):
        await query.edit_message_text("Sorry, that slot was just taken. Try /book again.")
        return ConversationHandler.END

    booking_id = db.create_booking(
        user_id=user.id,
        username=user.username or user.first_name,
        service=service_key,
        slot_date=slot_date,
        slot_time=slot_time,
    )

    await query.edit_message_text(
        "✅ Booking confirmed!\n\n"
        f"Reference: #{booking_id}\n"
        f"🛎 {SERVICES[service_key]}\n"
        f"📅 {slot_date}\n"
        f"⏰ {slot_time}\n\n"
        "See your bookings any time with /my_bookings."
    )
    context.user_data.clear()
    return ConversationHandler.END


async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Booking flow cancelled.")
    context.user_data.clear()
    return ConversationHandler.END


async def my_bookings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    rows = db.get_user_bookings(update.effective_user.id)
    if not rows:
        await update.message.reply_text("You have no active bookings. Use /book to make one.")
        return

    for row in rows:
        keyboard = [[InlineKeyboardButton("Cancel this booking", callback_data=f"cancel:{row['id']}")]]
        await update.message.reply_text(
            f"#{row['id']} — {SERVICES.get(row['service'], row['service'])}\n"
            f"📅 {row['slot_date']}  ⏰ {row['slot_time']}",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )


async def cancel_booking_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    booking_id = int(query.data.split(":", 1)[1])
    ok = db.cancel_booking(booking_id, update.effective_user.id)
    if ok:
        await query.edit_message_text(f"Booking #{booking_id} cancelled.")
    else:
        await query.edit_message_text("Couldn't cancel that booking.")


def build_conversation_handler():
    return ConversationHandler(
        entry_points=[CommandHandler("start", start), CommandHandler("book", start)],
        states={
            CHOOSING_SERVICE: [CallbackQueryHandler(service_chosen, pattern=r"^svc:")],
            CHOOSING_DATE: [CallbackQueryHandler(date_chosen, pattern=r"^date:")],
            CHOOSING_TIME: [CallbackQueryHandler(time_chosen, pattern=r"^time:")],
            CONFIRMING: [CallbackQueryHandler(confirm, pattern=r"^confirm:")],
        },
        fallbacks=[CommandHandler("cancel", cancel_command)],
    )
