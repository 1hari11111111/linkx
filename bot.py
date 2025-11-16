import time
import asyncio
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

from config import BOT_TOKEN, ADMINS
from database import init_db, is_approved, approve, block, get_all
from bypass.simple import direct_bypass
from bypass.pixeldrain import pixeldrain_bypass
from bypass.universal import universal_bypass
from bypass.arolinks import arolinks_bypass
from bypass.vplinks import vplinks_bypass
from playwright_engine.browser import browser_bypass

# Initialize database
init_db()


# ----------------------------
# /start
# ----------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id

    if uid in ADMINS:
        await update.message.reply_text(
            "👑 Hello Admin!\nSend any link to bypass."
        )
        return

    if not is_approved(uid):
        await update.message.reply_text(
            "❌ You are not approved.\nRequest sent to Admin."
        )
        for admin in ADMINS:
            try:
                await context.bot.send_message(
                    admin, f"🔔 User *{uid}* is requesting access.", parse_mode="Markdown"
                )
            except:
                pass
        return

    await update.message.reply_text("Send me any link to bypass 🔗")


# ----------------------------
# Admin: /approve
# ----------------------------
async def approve_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id

    if uid not in ADMINS:
        return

    try:
        target = int(context.args[0])
        approve(target)
        await update.message.reply_text(f"✅ Approved user: {target}")
    except:
        await update.message.reply_text("Usage: /approve <userid>")


# ----------------------------
# Admin: /block
# ----------------------------
async def block_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id

    if uid not in ADMINS:
        return

    try:
        target = int(context.args[0])
        block(target)
        await update.message.reply_text(f"❌ Blocked user: {target}")
    except:
        await update.message.reply_text("Usage: /block <userid>")


# ----------------------------
# Admin: /approved
# ----------------------------
async def approved_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMINS:
        return

    rows = get_all()
    msg = "📋 *Approved / Blocked Users:*\n\n"
    for uid, status in rows:
        msg += f"`{uid}` — {'✅ Approved' if status == 1 else '❌ Blocked'}\n"

    await update.message.reply_text(msg, parse_mode="Markdown")


# ----------------------------
# BYPASS HANDLER
# ----------------------------
async def bypass_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    text = update.message.text.strip()

    # Block non-approved users
    if uid not in ADMINS and not is_approved(uid):
        await update.message.reply_text("❌ You are not approved to use this bot.")
        return

    start_time = time.time()
    result = None

    # ----------------------------
    # 1 — SPECIAL SHORTENER HANDLERS
    # ----------------------------

    # AroLinks
    if "arolinks.com" in text:
        result = await arolinks_bypass(text)

    # VPLinks
    if not result and ("vplinks.in" in text or "vplinks" in text):
        result = await vplinks_bypass(text)

    # PixelDrain
    if not result and ("pixeldrain.com" in text):
        result = pixeldrain_bypass(text)

    # ----------------------------
    # 2 — DIRECT FAST BYPASS
    # ----------------------------
    if not result:
        result = direct_bypass(text)

    # ----------------------------
    # 3 — UNIVERSAL FALLBACK
    # ----------------------------
    if not result:
        result = universal_bypass(text)

    # ----------------------------
    # 4 — BROWSER PLAYWRIGHT (guaranteed)
    # ----------------------------
    if not result or result == text:
        result = await browser_bypass(text)

    end_time = round(time.time() - start_time, 2)

    # ----------------------------
    # SEND RESULT
    # ----------------------------
    if not result:
        await update.message.reply_text("❌ Failed to bypass this link.")
        return

    msg = f"""
🔓 <b>Bypass Successful</b>

<b>Original:</b> {text}
<b>Final:</b> {result}

⏱️ <b>Time Taken:</b> {end_time}s
"""
    await update.message.reply_text(msg, parse_mode="HTML")


# ----------------------------
# START BOT
# ----------------------------
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("approve", approve_cmd))
    app.add_handler(CommandHandler("block", block_cmd))
    app.add_handler(CommandHandler("approved", approved_list))

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, bypass_handler))

    app.run_polling()


if __name__ == "__main__":
    main()

