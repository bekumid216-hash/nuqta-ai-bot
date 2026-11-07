# Nuqta AI tashxis boti: ishga tushirish (15 daqiqa)

1. Zip'ni oching, papka ichida manzil satriga `cmd` yozib Enter bosing.
2. O'rnating:   py -3.12 -m pip install python-telegram-bot
3. Token: Telegram'da @BotFather -> /mybots -> NuqtaAI_bot -> API Token -> Copy.
   TOKENNI HECH KIMGA KO'RSATMANG (menga ham). Sizib chiqsa: BotFather -> /revoke.
   Buyruq oynasida:   setx BOT_TOKEN "bu-yerga-token"     (keyin oynani yopib, yangisini oching)
4. Ishga tushirish:   py -3.12 nuqta_tashxis_bot.py
   "Bot ishga tushdi" chiqsa, t.me/NuqtaAI_bot ga kirib /start bosing va o'zingiz mijoz sifatida 1 marta o'ting.
5. Lid xabarlari o'zingizga kelishi uchun: botga /id yozing, chiqqan raqamni nusxalang.
   Bot oynasini Ctrl+C bilan to'xtating, keyin:
   setx OWNER_CHAT_ID "raqam"    -> oynani qayta oching -> 4-qadamni takrorlang.
   (Guruhga yuborish uchun botni guruhga qo'shing, guruhda /id yozing.)

Bloger havolalari (qaysi bloger nechta lid olib kelganini ko'rish uchun):
   https://t.me/NuqtaAI_bot?start=bloger1   (bloger2, bloger3 ...) -> leadlar.csv dagi "manba" ustuni.

Bilib qo'ying:
- Bot kompyuteringiz yoqiq va internet ulangan, oyna ochiq turganda ishlaydi. Keyin arzon serverga ko'chiramiz.
- Barcha lidlar leadlar.csv da (Excel'da ochiladi). /stat (faqat egasi uchun) lidlar sonini ko'rsatadi.
- Savol va tavsiyalar nuqta_tashxis_bot.py ichida (Q va AREAS). Ularni birga yaxshilaymiz.
- Tashxis qoidalaridagi ball chegaralari va "issiq/iliq/sovuq" mezoni bizning gipotezamiz, haqiqiy lidlar bilan tuzatamiz.

---
# KANALGA AVTOMATIK POST (har kuni 09:00 va 18:00, Toshkent vaqti)

1. Botni kanalga ADMIN qiling: kanal -> Boshqaruv (Administrators) -> Admin qo'shish -> @NuqtaAI_bot -> "Post messages" (xabar joylash) ruxsatini yoqing.
2. Kanal nomi odatda @nuqta_ai. Boshqacha bo'lsa: setx CHANNEL_ID "@boshqa_nom" (oynani qayta oching).
3. OWNER_CHAT_ID (yuqorida) o'rnatilgan bo'lishi shart: bot sizga har joylangan post va xatolar haqida yozadi.
4. postlar.txt ni oching: 14 ta tayyor post bor, har biri ===== qatori bilan ajratilgan.
   - 1-post tanishuv posti. Agar uni kanalga allaqachon qo'lda joylagan bo'lsangiz, fayldan o'sha blokni o'chiring.
   - Yangi post qo'shish: oxiriga ===== yozib, keyin matnni yozing. Qalin yozuv: <b>matn</b>. "<", ">" va "&" belgilarini ishlatmang.
   - Rasm qo'shish (ixtiyoriy): post boshiga alohida qatorda  #rasm: rasmlar\1.png
5. Botni qayta ishga tushiring: py -3.12 nuqta_tashxis_bot.py  ("Kanal avto-post yoqilgan" chiqishi kerak).

Egasi uchun buyruqlar (botga shaxsiy yozing):
  /post_korish  - keyingi postni avval o'zingizga ko'rsatadi (kanalga chiqmaydi)
  /post_hozir   - keyingi postni darhol kanalga joylaydi
  /post_pauza   - avto-postni to'xtatadi      /post_davom - davom ettiradi
  /post_holat   - nechta post qolgan va keyingi vaqt

Bilib qo'ying:
- Kompyuter yoqiq, internet ulangan va bot oynasi ochiq bo'lishi kerak. Kompyuter 09:00 da o'chiq bo'lsa, yoqilgach 30 daqiqagacha hali joylaydi, keyin o'tkazib yuboradi (qo'lda /post_hozir).
- Postlar tugasa, bot sizga yozadi va yangisini kutadi; avtomat hech narsa o'ylab topmaydi.
- Birinchi 1-2 kun /post_korish bilan har postni oldindan ko'rib chiqing.
