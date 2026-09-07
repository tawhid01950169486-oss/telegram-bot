import os
import json
import logging
from functools import wraps

from telegram import Update, ChatPermissions
from telegram.ext import (
    Application,
    CommandHandler,
    ChatMemberHandler,
    ContextTypes,
)

TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

DATA_FILE = "data.json"


def load_data():
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {
            "welcome": {},
            "goodbye": {},
            "rules": {},
            "filters": {},
            "blacklist": {},
            "warnings": {},
            "stats": {},
        }


data = load_data()


def save_data():
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


async def admin_only(update: Update):
    if not update.effective_chat or not update.effective_user:
        return False

    try:
        member = await update.effective_chat.get_member(
            update.effective_user.id
        )
        return member.status in ("administrator", "creator")
    except Exception:
        return False


def target_user(update: Update):
    if update.message and update.message.reply_to_message:
        return update.message.reply_to_message.from_user
    return None


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 আসসালামু আলাইকুম!\n\n"
        "🤖 আমি আপনার Group Management Bot.\n\n"
        "📋 /help — সব Command দেখুন\n"
        "📜 /rules — Group Rules দেখুন\n"
        "⚡ /ping — Bot Status"
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 ꧁༺ GROUP MANAGEMENT BOT ༻꧂\n\n"

        "🛡️ MODERATION\n"
        "/ban — Ban a user\n"
        "/unban USER_ID — Unban a user\n"
        "/kick — Kick a user\n"
        "/mute — Mute a user\n"
        "/unmute — Unmute a user\n"
        "/warn — Warn a user\n"
        "/unwarn — Remove warning\n"
        "/del — Delete replied message\n"
        "/purge — Delete messages\n\n"

        "👑 ADMIN\n"
        "/promote — Promote user\n"
        "/demote — Demote user\n"
        "/admins — Show admins\n"
        "/reload — Reload admin list\n\n"

        "📌 PIN\n"
        "/pin — Pin replied message\n"
        "/unpin — Unpin message\n\n"

        "👋 WELCOME\n"
        "/welcome — Welcome settings\n"
        "/setwelcome TEXT — Set welcome\n"
        "/goodbye — Goodbye settings\n"
        "/setgoodbye TEXT — Set goodbye\n\n"

        "📜 RULES\n"
        "/rules — Show rules\n"
        "/setrules TEXT — Set rules\n\n"

        "🚫 FILTER\n"
        "/filter WORD TEXT — Add filter\n"
        "/stop WORD — Remove filter\n"
        "/filters — List filters\n\n"

        "🛡️ PROTECTION\n"
        "/antispam — Anti-spam settings\n"
        "/antiflood — Anti-flood settings\n"
        "/captcha — Captcha settings\n"
        "/blacklist — Blacklist settings\n"
        "/whitelist — Whitelist settings\n\n"

        "🔒 LOCK\n"
        "/lock TYPE — Lock content type\n"
        "/unlock TYPE — Unlock content type\n"
        "/locktypes — Locked types\n"
        "/clean — Clean messages\n\n"

        "✅ APPROVAL\n"
        "/approve — Approve user\n"
        "/unapprove — Remove approval\n\n"

        "ℹ️ OTHER\n"
        "/id — User/Chat ID\n"
        "/info — User information\n"
        "/settings — Bot settings\n"
        "/stats — Bot statistics\n"
        "/ping — Check bot status\n"
        "/about — About bot"
    )


async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 My Telegram Group Management Bot\n\n"
        "🛡️ Group moderation & protection\n"
        "⚡ Python powered\n"
        "💙 Made for Telegram Groups"
    )


async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🏓 Pong!\n\n✅ Bot is Online.")


async def id_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat = update.effective_chat

    await update.message.reply_text(
        f"👤 User ID: `{user.id}`\n"
        f"💬 Chat ID: `{chat.id}`",
        parse_mode="Markdown",
    )


async def info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    username = (
        f"@{user.username}"
        if user.username
        else "None"
    )

    await update.message.reply_text(
        f"👤 Name: {user.full_name}\n"
        f"🆔 ID: `{user.id}`\n"
        f"🔗 Username: {username}",
        parse_mode="Markdown",
    )


async def rules_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.effective_chat.id)

    text = data["rules"].get(
        chat_id,
        "📜 এই গ্রুপের Rules এখনো সেট করা হয়নি।"
    )

    await update.message.reply_text(text)


async def setrules(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await admin_only(update):
        return await update.message.reply_text("❌ Admin only.")

    if not context.args:
        return await update.message.reply_text(
            "ব্যবহার:\n/setrules আপনার গ্রুপের Rules"
        )

    chat_id = str(update.effective_chat.id)
    data["rules"][chat_id] = "📜 GROUP RULES\n\n" + " ".join(context.args)
    save_data()

    await update.message.reply_text("✅ Group Rules সেট করা হয়েছে।")


async def welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.effective_chat.id)

    text = data["welcome"].get(
        chat_id,
        "👋 Welcome settings চালু আছে।"
    )

    await update.message.reply_text(text)


async def setwelcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await admin_only(update):
        return await update.message.reply_text("❌ Admin only.")

    if not context.args:
        return await update.message.reply_text(
            "ব্যবহার:\n/setwelcome 👋 Welcome {name}!"
        )

    chat_id = str(update.effective_chat.id)

    data["welcome"][chat_id] = " ".join(context.args)
    save_data()

    await update.message.reply_text(
        "✅ Welcome message সেট করা হয়েছে।"
    )


async def goodbye(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.effective_chat.id)

    text = data["goodbye"].get(
        chat_id,
        "👋 Goodbye settings চালু আছে।"
    )

    await update.message.reply_text(text)


async def setgoodbye(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await admin_only(update):
        return await update.message.reply_text("❌ Admin only.")

    if not context.args:
        return await update.message.reply_text(
            "ব্যবহার:\n/setgoodbye 👋 Goodbye {name}!"
        )

    chat_id = str(update.effective_chat.id)

    data["goodbye"][chat_id] = " ".join(context.args)
    save_data()

    await update.message.reply_text(
        "✅ Goodbye message সেট করা হয়েছে।"
    )


async def ban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await admin_only(update):
        return await update.message.reply_text("❌ Admin only.")

    target = target_user(update)

    if not target:
        return await update.message.reply_text(
            "❌ যাকে Ban করবেন তার message-এ Reply করে /ban দিন।"
        )

    try:
        await update.effective_chat.ban_member(target.id)

        await update.message.reply_text(
            f"🔨 {target.full_name} কে Ban করা হয়েছে।"
        )
    except Exception as e:
        await update.message.reply_text(
            f"❌ Ban করা যায়নি:\n{e}"
        )


async def unban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await admin_only(update):
        return await update.message.reply_text("❌ Admin only.")

    if not context.args:
        return await update.message.reply_text(
            "ব্যবহার:\n/unban USER_ID"
        )

    try:
        user_id = int(context.args[0])

        await update.effective_chat.unban_member(user_id)

        await update.message.reply_text(
            "✅ User Unban করা হয়েছে।"
        )
    except Exception:
        await update.message.reply_text(
            "❌ সঠিক User ID দিন।"
        )


async def kick(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await admin_only(update):
        return await update.message.reply_text("❌ Admin only.")

    target = target_user(update)

    if not target:
        return await update.message.reply_text(
            "❌ Member-এর message-এ Reply করে /kick দিন।"
        )

    try:
        await update.effective_chat.ban_member(target.id)
        await update.effective_chat.unban_member(target.id)

        await update.message.reply_text(
            f"👢 {target.full_name} কে Kick করা হয়েছে।"
        )
    except Exception as e:
        await update.message.reply_text(
            f"❌ Kick করা যায়নি:\n{e}"
        )


async def mute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await admin_only(update):
        return await update.message.reply_text("❌ Admin only.")

    target = target_user(update)

    if not target:
        return await update.message.reply_text(
            "❌ Member-এর message-এ Reply করে /mute দিন।"
        )

    try:
        await update.effective_chat.restrict_member(
            target.id,
            ChatPermissions(can_send_messages=False),
        )

        await update.message.reply_text(
            f"🔇 {target.full_name} কে Mute করা হয়েছে।"
        )
    except Exception as e:
        await update.message.reply_text(
            f"❌ Mute করা যায়নি:\n{e}"
        )


async def unmute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await admin_only(update):
        return await update.message.reply_text("❌ Admin only.")

    target = target_user(update)

    if not target:
        return await update.message.reply_text(
            "❌ Member-এর message-এ Reply করে /unmute দিন।"
        )

    try:
        permissions = ChatPermissions(
            can_send_messages=True,
            can_send_audios=True,
            can_send_documents=True,
            can_send_photos=True,
            can_send_videos=True,
            can_send_video_notes=True,
            can_send_voice_notes=True,
            can_send_polls=True,
            can_send_other_messages=True,
            can_add_web_page_previews=True,
        )

        await update.effective_chat.restrict_member(
            target.id,
            permissions=permissions,
        )

        await update.message.reply_text(
            f"🔊 {target.full_name} এর Mute তুলে দেওয়া হয়েছে।"
        )
    except Exception as e:
        await update.message.reply_text(
            f"❌ Unmute করা যায়নি:\n{e}"
        )


async def warn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await admin_only(update):
        return await update.message.reply_text("❌ Admin only.")

    target = target_user(update)

    if not target:
        return await update.message.reply_text(
            "❌ Member-এর message-এ Reply করে /warn দিন।"
        )

    chat_id = str(update.effective_chat.id)
    key = f"{chat_id}:{target.id}"

    data["warnings"][key] = data["warnings"].get(key, 0) + 1
    count = data["warnings"][key]

    save_data()

    await update.message.reply_text(
        f"⚠️ {target.full_name} কে Warning দেওয়া হয়েছে।\n"
        f"📊 Warning: {count}/3"
    )

    if count >= 3:
        try:
            await update.effective_chat.ban_member(target.id)

            await update.message.reply_text(
                f"🔨 3টি Warning পূর্ণ হওয়ায় "
                f"{target.full_name} Ban করা হয়েছে।"
            )
        except Exception:
            pass


async def unwarn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await admin_only(update):
        return await update.message.reply_text("❌ Admin only.")

    target = target_user(update)

    if not target:
        return await update.message.reply_text(
            "❌ Member-এর message-এ Reply করে /unwarn দিন।"
        )

    key = f"{update.effective_chat.id}:{target.id}"

    current = data["warnings"].get(key, 0)

    if current > 0:
        data["warnings"][key] = current - 1

    save_data()

    await update.message.reply_text(
        f"✅ Warning কমানো হয়েছে।\n"
        f"📊 Warning: {data['warnings'].get(key, 0)}"
    )


async def warnings_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    target = target_user(update) or update.effective_user

    key = f"{update.effective_chat.id}:{target.id}"

    count = data["warnings"].get(key, 0)

    await update.message.reply_text(
        f"⚠️ {target.full_name}\n"
        f"📊 Warning: {count}/3"
    )


async def delete_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await admin_only(update):
        return await update.message.reply_text("❌ Admin only.")

    if not update.message.reply_to_message:
        return await update.message.reply_text(
            "❌ যে message delete করবেন সেটিতে Reply করে /del দিন।"
        )

    try:
        await update.message.reply_to_message.delete()
        await update.message.delete()
    except Exception:
        pass


async def purge(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await admin_only(update):
        return await update.message.reply_text("❌ Admin only.")

    await update.message.reply_text(
        "🧹 Purge ব্যবহার করতে message range-এর জন্য আরও উন্নত "
        "message-ID system প্রয়োজন।"
    )


async def pin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await admin_only(update):
        return await update.message.reply_text("❌ Admin only.")

    if not update.message.reply_to_message:
        return await update.message.reply_text(
            "❌ যে message Pin করবেন সেটিতে Reply করে /pin দিন।"
        )

    try:
        await update.message.reply_to_message.pin()
        await update.message.reply_text("📌 Message Pin করা হয়েছে।")
    except Exception as e:
        await update.message.reply_text(
            f"❌ Pin করা যায়নি:\n{e}"
        )


async def unpin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await admin_only(update):
        return await update.message.reply_text("❌ Admin only.")

    try:
        await update.effective_chat.unpin_all_messages()
        await update.message.reply_text("📌 সব Pin তুলে দেওয়া হয়েছে।")
    except Exception as e:
        await update.message.reply_text(
            f"❌ Unpin করা যায়নি:\n{e}"
        )


async def admins(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        administrators = await update.effective_chat.get_administrators()

        text = "👑 GROUP ADMINS\n\n"

        for admin in administrators:
            text += f"• {admin.user.full_name}\n"

        await update.message.reply_text(text)

    except Exception as e:
        await update.message.reply_text(
            f"❌ Admin list পাওয়া যায়নি:\n{e}"
        )


async def promote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await admin_only(update):
        return await update.message.reply_text("❌ Admin only.")

    target = target_user(update)

    if not target:
        return await update.message.reply_text(
            "❌ Member-এর message-এ Reply করে /promote দিন।"
        )

    try:
        await update.effective_chat.promote_member(
            target.id,
            can_manage_chat=True,
            can_delete_messages=True,
            can_restrict_members=True,
            can_invite_users=True,
            can_pin_messages=True,
            can_manage_video_chats=True,
        )

        await update.message.reply_text(
            f"👑 {target.full_name} কে Admin করা হয়েছে।"
        )
    except Exception as e:
        await update.message.reply_text(
            f"❌ Promote করা যায়নি:\n{e}"
        )


async def demote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await admin_only(update):
        return await update.message.reply_text("❌ Admin only.")

    target = target_user(update)

    if not target:
        return await update.message.reply_text(
            "❌ Admin-এর message-এ Reply করে /demote দিন।"
        )

    try:
        await update.effective_chat.promote_member(
            target.id,
            can_manage_chat=False,
            can_delete_messages=False,
            can_restrict_members=False,
            can_invite_users=False,
            can_pin_messages=False,
            can_manage_video_chats=False,
        )

        await update.message.reply_text(
            f"⬇️ {target.full_name} এর Admin permissions সরানো হয়েছে।"
        )
    except Exception as e:
        await update.message.reply_text(
            f"❌ Demote করা যায়নি:\n{e}"
        )


async def reload_admins(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🔄 Admin list reload করা হয়েছে।"
    )


async def settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "⚙️ BOT SETTINGS\n\n"
        "👋 Welcome: Available\n"
        "🚪 Goodbye: Available\n"
        "📜 Rules: Available\n"
        "⚠️ Warning: 3 strikes\n"
        "🛡️ Moderation: Available"
    )


async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📊 BOT STATISTICS\n\n"
        "🤖 Status: Online\n"
        "⚡ Mode: Polling\n"
        "🛡️ Moderation: Active"
    )


async def filter_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await admin_only(update):
        return await update.message.reply_text("❌ Admin only.")

    if len(context.args) < 2:
        return await update.message.reply_text(
            "ব্যবহার:\n/filter word response"
        )

    word = context.args[0].lower()
    response = " ".join(context.args[1:])

    chat_id = str(update.effective_chat.id)

    if chat_id not in data["filters"]:
        data["filters"][chat_id] = {}

    data["filters"][chat_id][word] = response
    save_data()

    await update.message.reply_text(
        f"✅ Filter added: {word}"
    )


async def stop_filter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await admin_only(update):
        return await update.message.reply_text("❌ Admin only.")

    if not context.args:
        return await update.message.reply_text(
            "ব্যবহার:\n/stop word"
        )

    word = context.args[0].lower()
    chat_id = str(update.effective_chat.id)

    if (
        chat_id in data["filters"]
        and word in data["filters"][chat_id]
    ):
        del data["filters"][chat_id][word]
        save_data()

        await update.message.reply_text(
            f"✅ Filter removed: {word}"
        )
    else:
        await update.message.reply_text(
            "❌ এই Filter পাওয়া যায়নি।"
        )


async def filters_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.effective_chat.id)

    filters = data["filters"].get(chat_id, {})

    if not filters:
        return await update.message.reply_text(
            "📋 কোনো Filter সেট করা নেই।"
        )

    text = "📋 FILTERS\n\n"

    for word in filters:
        text += f"• {word}\n"

    await update.message.reply_text(text)


async def antispam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await admin_only(update):
        return await update.message.reply_text("❌ Admin only.")

    await update.message.reply_text(
        "🛡️ Anti-Spam system command received.\n"
        "Advanced automatic spam detection পরে চালু করা যাবে।"
    )


async def antiflood(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await admin_only(update):
        return await update.message.reply_text("❌ Admin only.")

    await update.message.reply_text(
        "🌊 Anti-Flood settings command received."
    )


async def lock(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await admin_only(update):
        return await update.message.reply_text("❌ Admin only.")

    if not context.args:
        return await update.message.reply_text(
            "ব্যবহার:\n/lock TYPE\n\n"
            "Example: /lock links"
        )

    await update.message.reply_text(
        f"🔒 {context.args[0]} lock command received."
    )


async def unlock(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await admin_only(update):
        return await update.message.reply_text("❌ Admin only.")

    if not context.args:
        return await update.message.reply_text(
            "ব্যবহার:\n/unlock TYPE"
        )

    await update.message.reply_text(
        f"🔓 {context.args[0]} unlock command received."
    )


async def clean(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await admin_only(update):
        return await update.message.reply_text("❌ Admin only.")

    await update.message.reply_text(
        "🧹 Clean command received."
    )


async def captcha(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await admin_only(update):
        return await update.message.reply_text("❌ Admin only.")

    await update.message.reply_text(
        "🤖 Captcha settings command received."
    )


async def blacklist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await admin_only(update):
        return await update.message.reply_text("❌ Admin only.")

    await update.message.reply_text(
        "🚫 Blacklist settings command received."
    )


async def whitelist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await admin_only(update):
        return await update.message.reply_text("❌ Admin only.")

    await update.message.reply_text(
        "✅ Whitelist settings command received."
    )


async def locktypes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🔒 LOCKED CONTENT TYPES\n\n"
        "এখনো কোনো content type lock করা হয়নি।"
    )


async def approve(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await admin_only(update):
        return await update.message.reply_text("❌ Admin only.")

    target = target_user(update)

    if not target:
        return await update.message.reply_text(
            "❌ Member-এর message-এ Reply করে /approve দিন।"
        )

    await update.message.reply_text(
        f"✅ {target.full_name} Approved."
    )


async def unapprove(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await admin_only(update):
        return await update.message.reply_text("❌ Admin only.")

    target = target_user(update)

    if not target:
        return await update.message.reply_text(
            "❌ Member-এর message-এ Reply করে /unapprove দিন।"
        )

    await update.message.reply_text(
        f"❌ {target.full_name} এর approval removed."
    )


async def message_filter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    chat_id = str(update.effective_chat.id)
    text = update.message.text.lower()

    filters = data["filters"].get(chat_id, {})

    for word, response in filters.items():
        if word in text:
            try:
                await update.message.reply_text(response)
            except Exception:
                pass
            break


async def new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.chat_member:
        return

    member = update.chat_member.new_chat_member

    if member.status not in ("member", "restricted"):
        return

    user = member.user
    chat_id = str(update.effective_chat.id)

    text = data["welcome"].get(
        chat_id,
        "👋 Welcome {name}!"
    )

    text = text.replace("{name}", user.full_name)

    if user.username:
        text = text.replace(
            "{username}",
            f"@{user.username}"
        )
    else:
        text = text.replace(
            "{username}",
            user.full_name
        )

    await context.bot.send_message(
        update.effective_chat.id,
        text
    )


async def left_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.chat_member:
        return

    member = update.chat_member.new_chat_member

    if member.status not in ("left", "kicked"):
        return

    user = member.user
    chat_id = str(update.effective_chat.id)

    text = data["goodbye"].get(
        chat_id,
        "👋 Goodbye {name}!"
    )

    text = text.replace("{name}", user.full_name)

    if user.username:
        text = text.replace(
            "{username}",
            f"@{user.username}"
        )
    else:
        text = text.replace(
            "{username}",
            user.full_name
        )

    await context.bot.send_message(
        update.effective_chat.id,
        text
    )


def main():
    if not TOKEN:
        raise RuntimeError(
            "BOT_TOKEN environment variable is missing."
        )

    app = Application.builder().token(TOKEN).build()

    # Basic
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("about", about))
    app.add_handler(CommandHandler("ping", ping))

    # Information
    app.add_handler(CommandHandler("id", id_command))
    app.add_handler(CommandHandler("info", info))
    app.add_handler(CommandHandler("admins", admins))
    app.add_handler(CommandHandler("reload", reload_admins))
    app.add_handler(CommandHandler("settings", settings))
    app.add_handler(CommandHandler("stats", stats))

    # Rules
    app.add_handler(CommandHandler("rules", rules_command))
    app.add_handler(CommandHandler("setrules", setrules))

    # Welcome
    app.add_handler(CommandHandler("welcome", welcome))
    app.add_handler(CommandHandler("setwelcome", setwelcome))
    app.add_handler(CommandHandler("goodbye", goodbye))
    app.add_handler(CommandHandler("setgoodbye", setgoodbye))

    # Moderation
    app.add_handler(CommandHandler("ban", ban))
    app.add_handler(CommandHandler("unban", unban))
    app.add_handler(CommandHandler("kick", kick))
    app.add_handler(CommandHandler("mute", mute))
    app.add_handler(CommandHandler("unmute", unmute))
    app.add_handler(CommandHandler("warn", warn))
    app.add_handler(CommandHandler("unwarn", unwarn))
    app.add_handler(CommandHandler("warnings", warnings_command))

    # Messages
    app.add_handler(CommandHandler("del", delete_message))
    app.add_handler(CommandHandler("purge", purge))
    app.add_handler(CommandHandler("pin", pin))
    app.add_handler(CommandHandler("unpin", unpin))

    # Admin
    app.add_handler(CommandHandler("promote", promote))
    app.add_handler(CommandHandler("demote", demote))

    # Filters
    app.add_handler(CommandHandler("filter", filter_command))
    app.add_handler(CommandHandler("stop", stop_filter))
    app.add_handler(CommandHandler("filters", filters_command))

    # Protection
    app.add_handler(CommandHandler("antispam", antispam))
    app.add_handler(CommandHandler("antiflood", antiflood))
    app.add_handler(CommandHandler("captcha", captcha))
    app.add_handler(CommandHandler("blacklist", blacklist))
    app.add_handler(CommandHandler("whitelist", whitelist))

    # Lock
    app.add_handler(CommandHandler("lock", lock))
    app.add_handler(CommandHandler("unlock", unlock))
    app.add_handler(CommandHandler("clean", clean))
    app.add_handler(CommandHandler("locktypes", locktypes))

    # Approval
    app.add_handler(CommandHandler("approve", approve))
    app.add_handler(CommandHandler("unapprove", unapprove))

    # Member events
    app.add_handler(
        ChatMemberHandler(
            new_member,
            ChatMemberHandler.CHAT_MEMBER
        )
    )

    app.add_handler(
        ChatMemberHandler(
            left_member,
            ChatMemberHandler.CHAT_MEMBER
        )
    )

    # Text filters
    from telegram.ext import MessageHandler, filters

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            message_filter
        )
    )

    print("🤖 Bot is running...")

    app.run_polling()


if __name__ == "__main__":
    main()
