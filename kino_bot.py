import json
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

BOT_TOKEN = "8538645649:AAHVWz7OZ0k7FdoLqAiuI3ihnEsihu7LQDA"
ADMIN_ID = 5660330328

CHANNELS = [
    "@Uzb_yangiliklari_qora_habarlar",
    "@Fudbol_tv_fudbol_yangiliklari",
    "@Uztop_Kinolar"
]

INSTAGRAM_URL = "https://instagram.com/uztop_kinolar"

DATA_FILE = "kino_data.json"
USERS_FILE = "users.json"
BLOCK_FILE = "block.json"

REKLAMA_MODE = {}

# ================= JSON =================
def load_json(file, default):
    if not os.path.exists(file):
        return default
    with open(file, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(file, data):
    with open(file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ================= OBUNA =================
async def is_subscribed(user_id, context):
    for ch in CHANNELS:
        try:
            member = await context.bot.get_chat_member(ch, user_id)
            if member.status not in ("member", "administrator", "creator"):
                return False
        except:
            return False
    return True

def subscribe_keyboard():
    btn = []
    for i, ch in enumerate(CHANNELS):
        btn.append([InlineKeyboardButton(f"📢 Kanal {i+1}", url=f"https://t.me/{ch[1:]}")])
    btn.append([InlineKeyboardButton("✅ Tekshirish", callback_data="check_sub")])
    return InlineKeyboardMarkup(btn)

def main_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📷 Instagram", url=INSTAGRAM_URL)],
        [InlineKeyboardButton("🤝 Ulashish", switch_inline_query="Top Kinolar")]
    ])

# ================= START =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    blocked = load_json(BLOCK_FILE, [])
    if user.id in blocked:
        return

    users = load_json(USERS_FILE, {})
    users[str(user.id)] = user.username or "no_username"
    save_json(USERS_FILE, users)

    if not await is_subscribed(user.id, context):
        await update.message.reply_text(
            "🔐 Kanallarga obuna bo‘ling:",
            reply_markup=subscribe_keyboard()
        )
        return

    text = (
        "🎬 <b>TOP KINOLAR BOTIGA XUSH KELIBSIZ!</b>\n\n"
        "🔥 Eng yangi kinolar\n"
        "🔑 Maxsus KINO KODLARI orqali\n"
        "⚡ Tez va qulay tomosha\n\n"
        "📌 Foydalanish:\n"
        "👉 Kino kodini yuboring (masalan: K001)\n\n"
        "🎥 Har kuni yangi kinolar qo‘shiladi!"
    )

    await update.message.reply_text(text, reply_markup=main_keyboard(), parse_mode="HTML")

# ================= CHECK =================
async def check_sub(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    if await is_subscribed(q.from_user.id, context):
        await q.message.edit_text(
            "✅ Obuna tasdiqlandi!\n\nKod yuboring 👇",
            reply_markup=main_keyboard()
        )
    else:
        await q.message.edit_text(
            "❌ Siz hali obuna bo‘lmadingiz!\n\n👇 Kanallarga kiring:",
            reply_markup=subscribe_keyboard()
        )

# ================= KINO =================
async def kino_kod(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    blocked = load_json(BLOCK_FILE, [])
    if user.id in blocked:
        return

    if not await is_subscribed(user.id, context):
        await update.message.reply_text(
            "❌ Siz kanallarga obuna bo‘lmagansiz!\n\n👇 Pastdagi tugmani bosing",
            reply_markup=subscribe_keyboard()
        )
        return

    code = update.message.text.strip().upper()
    data = load_json(DATA_FILE, {})

    if code not in data:
        await update.message.reply_text("❌ Kino topilmadi!")
        return

    movie = data[code]

    caption = (
        "🎬 <b>KINO TAYYOR!</b>\n\n"
        f"🔑 <b>Kod:</b> {code}\n\n"
        "🎥 Har kuni yangi kinolar\n"
        "📲 Instagram yangiliklar\n\n"
        "🤖 @UzTopKinolar_bot"
    )

    await update.message.reply_video(
        video=movie["file_id"],
        caption=caption,
        reply_markup=main_keyboard(),
        parse_mode="HTML"
    )

# ================= ADMIN VIDEO =================
async def admin_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    # 🔥 REKLAMA PAYTIDA KINO BO‘LIB KETMASIN
    if REKLAMA_MODE.get(update.effective_user.id):
        return

    if not update.message.video:
        return

    data = load_json(DATA_FILE, {})

    if not data:
        new_code = "K001"
    else:
        last = sorted(data.keys())[-1]
        num = int(last.replace("K", ""))
        new_code = f"K{num+1:03d}"

    data[new_code] = {
        "file_id": update.message.video.file_id
    }

    save_json(DATA_FILE, data)

    await update.message.reply_text(f"✅ Qo‘shildi: {new_code}")

# ================= DELETE =================
async def delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    if not context.args:
        await update.message.reply_text("❗ /delete K001")
        return

    code = context.args[0].upper()
    data = load_json(DATA_FILE, {})

    if code in data:
        del data[code]
        save_json(DATA_FILE, data)
        await update.message.reply_text(f"🗑 O‘chirildi: {code}")
    else:
        await update.message.reply_text("❌ Topilmadi")

# ================= USERS =================
async def users_count(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    users = load_json(USERS_FILE, {})
    await update.message.reply_text(f"👥 Userlar: {len(users)}")

# ================= BLOCK =================
async def block(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    user_id = int(context.args[0])
    blocked = load_json(BLOCK_FILE, [])

    if user_id not in blocked:
        blocked.append(user_id)
        save_json(BLOCK_FILE, blocked)

    await update.message.reply_text("🚫 Block qilindi")

async def unblock(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    user_id = int(context.args[0])
    blocked = load_json(BLOCK_FILE, [])

    if user_id in blocked:
        blocked.remove(user_id)
        save_json(BLOCK_FILE, blocked)

    await update.message.reply_text("✅ Unblock qilindi")

# ================= STAT =================
async def stat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    users = load_json(USERS_FILE, {})
    kino = load_json(DATA_FILE, {})

    await update.message.reply_text(
        f"📊 STAT\n👥 {len(users)}\n🎬 {len(kino)}"
    )

# ================= REKLAMA =================
async def reklama(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    REKLAMA_MODE[update.effective_user.id] = True
    await update.message.reply_text("📢 Reklama yubor")

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    REKLAMA_MODE[update.effective_user.id] = False
    await update.message.reply_text("❌ Bekor qilindi")

async def reklama_send(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not REKLAMA_MODE.get(update.effective_user.id):
        return

    users = load_json(USERS_FILE, {})
    ok, no = 0, 0

    for uid in users:
        try:
            uid = int(uid)

            if update.message.text:
                await context.bot.send_message(uid, update.message.text)

            elif update.message.photo:
                await context.bot.send_photo(
                    uid,
                    update.message.photo[-1].file_id,
                    caption=update.message.caption or ""
                )

            elif update.message.video:
                await context.bot.send_video(
                    uid,
                    update.message.video.file_id,
                    caption=update.message.caption or ""
                )

            ok += 1
        except:
            no += 1

    await update.message.reply_text(f"✅ {ok} | ❌ {no}")
    REKLAMA_MODE[update.effective_user.id] = False

# ================= MAIN =================
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stat", stat))
    app.add_handler(CommandHandler("reklama", reklama))
    app.add_handler(CommandHandler("cancel", cancel))
    app.add_handler(CommandHandler("delete", delete))
    app.add_handler(CommandHandler("users", users_count))
    app.add_handler(CommandHandler("block", block))
    app.add_handler(CommandHandler("unblock", unblock))

    app.add_handler(CallbackQueryHandler(check_sub, pattern="check_sub"))

    # 🔥 TO‘G‘RI TARTIB
    app.add_handler(MessageHandler(filters.Regex(r"^K\d+"), kino_kod))
    app.add_handler(MessageHandler(filters.VIDEO, admin_video))
    app.add_handler(MessageHandler(
        (filters.TEXT | filters.PHOTO | filters.VIDEO),
        reklama_send
    ))

    print("BOT ISHLADI")
    app.run_polling()

if __name__ == "__main__":
    main()