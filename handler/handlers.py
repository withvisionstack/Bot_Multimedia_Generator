from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)
from datetime import datetime, date, time, timedelta
import asyncio
import httpx

from handler.interface import comandos_rapidos


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Olá! Eu sou um bot. 👋",
        reply_markup=comandos_rapidos
    )