async def evaluate(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str, image_bytes: bytes | None) -> None:
    await update.message.chat.send_action("typing")

    contents = []
    if image_bytes:
        contents.append(types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg"))
    contents.append(text)

    try:
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=contents,
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
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
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


if name == "main":
    main()
