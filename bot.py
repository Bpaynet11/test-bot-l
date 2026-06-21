import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from google import genai
from google.genai import types

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# Token va API kalitlarni environment variable orqali olamiz (xavfsizlik uchun)
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

if not TELEGRAM_TOKEN or not GEMINI_API_KEY:
    raise RuntimeError(
        "TELEGRAM_BOT_TOKEN va GEMINI_API_KEY environment variable sifatida o'rnatilishi kerak."
    )

client = genai.Client(api_key=GEMINI_API_KEY)
GEMINI_MODEL = "gemini-2.5-flash"

SYSTEM_PROMPT = """Sen tajribali IELTS Writing examiner (baholovchi) san. Foydalanuvchi senga IELTS Writing
Task 1 yoki Task 2 matnini yuboradi (ba'zan vazifa shartini ham qo'shib yuboradi, ba'zan faqat insho matnini).

Vazifang:
1. Avval matn Task 1 (grafik/jadval/diagramma tasviri) yoki Task 2 (fikr-mulohaza insho) ekanligini aniqla.
2. Quyidagi 4 mezon bo'yicha baholang: Task Achievement/Response, Coherence and Cohesion,
   Lexical Resource, Grammatical Range and Accuracy.
3. Har bir mezon uchun taxminiy band (masalan 6.5, 7.0) va umumiy o'rtacha band score ber.
4. Eng muhim 2-4 ta xatoni aniq ko'rsat: xato qaysi qismda, nima uchun xato, va qanday tuzatish kerak
   (to'g'ri variantini yoz).
5. Matnning kuchli tomonlarini ham qisqa aytib o't.

Javobni FAQAT o'zbek tilida, qisqa va tushunarli formatda yoz (ortiqcha kirish so'zlarsiz, to'g'ridan-to'g'ri
baholashga o't). Telegram xabari sifatida o'qilishi qulay bo'lsin (qisqa paragraflar, kerak bo'lsa belgilar
bilan ro'yxat)."""


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Salom! IELTS Writing Task 1 yoki Task 2 matningizni shu yerga yuboring — "
        "men uni tekshirib, band score va asosiy xatolarni aytib beraman.\n\n"
        "Eslatma: agar Task 1 bo'lsa, jadval/grafik ma'lumotlarini ham matn ko'rinishida qo'shib yuborsangiz, "
        "baholash aniqroq bo'ladi."
    )


async def check_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_text = update.message.text

    if len(user_text.strip()) < 50:
        await update.message.reply_text(
            "Matn juda qisqa ko'rinadi. Iltimos, to'liq IELTS Writing javobingizni yuboring."
        )
        return

    await update.message.chat.send_action("typing")

    try:
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=user_text,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                max_output_tokens=2000,
            ),
        )
        reply = response.text
    except Exception as e:
        logger.exception("Gemini API xatosi")
        reply = f"Tekshirishda xatolik yuz berdi, birozdan keyin qaytadan urinib ko'ring.\n({e})"

    # Telegram xabar uzunligi cheklangani uchun (4096 belgi) bo'lib yuboramiz
    for i in range(0, len(reply), 4000):
        await update.message.reply_text(reply[i : i + 4000])


def main() -> None:
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, check_text))

    # Render.com kabi platformalarda RENDER_EXTERNAL_URL avtomatik beriladi.
    # Agar shu o'rnatilgan bo'lsa - webhook rejimida ishlaymiz (bepul Web Service uchun).
    # Aks holda (masalan kompyuterda lokal test qilganda) - polling rejimida ishlaymiz.
    webhook_base_url = os.environ.get("RENDER_EXTERNAL_URL") or os.environ.get("WEBHOOK_URL")
    port = int(os.environ.get("PORT", 8443))

    if webhook_base_url:
        logger.info("Webhook rejimida ishga tushdi: %s", webhook_base_url)
        app.run_webhook(
            listen="0.0.0.0",
            port=port,
            url_path="webhook",
            webhook_url=f"{webhook_base_url.rstrip('/')}/webhook",
        )
    else:
        logger.info("Polling rejimida (lokal) ishga tushdi...")
        app.run_polling()


if __name__ == "__main__":
    main()
