import os
import requests
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from bs4 import BeautifulSoup

BOT_TOKEN = os.environ.get("BOT_TOKEN", "8885327111:AAFDRRrmn25KbpXh1yb3e-BPbrW8Pv1ulDA")
bot = telebot.TeleBot(BOT_TOKEN)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
}

def search_imdb(movie_name):
    """Search IMDB and return the first result's ID and title."""
    query = movie_name.replace(" ", "+")
    url = f"https://www.imdb.com/find/?q={query}&s=tt&ttype=ft"
    try:
        res = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")

        # Try new IMDB layout
        results = soup.select("li.ipc-metadata-list-summary-item")
        for item in results:
            link = item.select_one("a.ipc-metadata-list-summary-item__t")
            if link and "/title/tt" in link.get("href", ""):
                href = link["href"]
                imdb_id = href.split("/title/")[1].split("/")[0]
                title = link.text.strip()
                return imdb_id, title

        # Fallback: old IMDB layout
        results = soup.select("td.result_text a")
        for r in results:
            href = r.get("href", "")
            if "/title/tt" in href:
                imdb_id = href.split("/title/")[1].split("/")[0]
                title = r.text.strip()
                return imdb_id, title

    except Exception as e:
        print(f"Search error: {e}")
    return None, None


@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(
        message.chat.id,
        "🎬 *مرحباً!*\n\nأرسل لي اسم أي فيلم وسأفتحه لك مباشرة للمشاهدة!\n\nمثال: `Inception` أو `The Dark Knight`",
        parse_mode="Markdown"
    )


@bot.message_handler(func=lambda m: True)
def handle_movie(message):
    movie_name = message.text.strip()

    # Send searching message
    searching_msg = bot.send_message(
        message.chat.id,
        f"🔍 جاري البحث عن: *{movie_name}*...",
        parse_mode="Markdown"
    )

    imdb_id, title = search_imdb(movie_name)

    if not imdb_id:
        bot.edit_message_text(
            "❌ لم أجد الفيلم. تأكد من الاسم وحاول مرة أخرى.",
            message.chat.id,
            searching_msg.message_id
        )
        return

    imdb_url = f"https://www.imdb.com/title/{imdb_id}/"
    watch_url = f"https://playimdb.com/{imdb_id}"

    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton(
            "▶️ شاهد الآن",
            web_app=WebAppInfo(url=watch_url)
        )
    )
    markup.add(
        InlineKeyboardButton("🎬 صفحة IMDB", url=imdb_url)
    )

    bot.edit_message_text(
        f"✅ *{title}*\n\n🔗 IMDB: `{imdb_id}`\n\nاضغط على الزر للمشاهدة:",
        message.chat.id,
        searching_msg.message_id,
        parse_mode="Markdown",
        reply_markup=markup
    )


if __name__ == "__main__":
    print("Bot started (polling)...")
    bot.infinity_polling()
