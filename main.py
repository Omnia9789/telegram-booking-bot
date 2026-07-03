import logging

from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler

from bot.config import BOT_TOKEN
from bot.database import init_db
from bot.handlers import build_conversation_handler, my_bookings, cancel_booking_callback

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)


def main():
    if not BOT_TOKEN:
        raise SystemExit("Set BOT_TOKEN in your .env file (see .env.example).")

    init_db()

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(build_conversation_handler())
    app.add_handler(CommandHandler("my_bookings", my_bookings))
    app.add_handler(CallbackQueryHandler(cancel_booking_callback, pattern=r"^cancel:"))

    print("Bot is running. Press Ctrl+C to stop.")
    app.run_polling()


if __name__ == "__main__":
    main()
