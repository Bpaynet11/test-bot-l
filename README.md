# IELTS Checker Bot

Bu Telegram bot IELTS Writing (Task 1 va Task 2) matnlarini tekshirib, band score va xatolarini o'zbek tilida aytib beradi.

## Kerakli ikkita kalit

1. **TELEGRAM_BOT_TOKEN** — Telegram'da @BotFather'ga yozib, `/newbot` orqali olinadi.
2. **GEMINI_API_KEY** — aistudio.google.com saytidan bepul olinadi (kartasiz).

## Render.com'da bepul joylashtirish

1. render.com'da hisob oching.
2. **New + → Blueprint** tugmasini bosing va shu GitHub repoyingizni tanlang (`render.yaml` fayli avtomatik topiladi).
3. So'ralganda quyidagi ikki maydonga yuqoridagi kalitlarni kiriting:
   - `TELEGRAM_BOT_TOKEN`
   - `GEMINI_API_KEY`
4. **Apply** / **Deploy** tugmasini bosing.

Bir necha daqiqadan keyin bot ishlay boshlaydi. Karta talab qilinmaydi.

**Eslatma:** bepul tarifda bot 15 daqiqa ishlatilmasa "uxlab qoladi", keyingi xabarga javob 30-60 soniya kechikadi — shaxsiy foydalanish uchun bu normal holat.
