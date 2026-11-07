#!/usr/bin/env python3
"""Nuqta AI | Biznes tashxis boti (Telegram).
Ishga tushirish:  py -3.12 nuqta_tashxis_bot.py
Kerak: BOT_TOKEN (9171846336:AAGxDjGoMhrFQFEX6K9Ish_yxw1kBly1lzo), OWNER_CHAT_ID (9206935719)
"""
import os, csv, html, re, datetime, json, asyncio
from pathlib import Path

try:
    from telegram import (InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup,
                          KeyboardButton, ReplyKeyboardRemove)
    from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
except ImportError:  # faqat mantiqni sinash uchun
    InlineKeyboardButton = InlineKeyboardMarkup = ReplyKeyboardMarkup = KeyboardButton = ReplyKeyboardRemove = None

BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER = os.getenv("OWNER_CHAT_ID")
LEADS = Path("leadlar.csv")

AREAS = {  # nom, sabab, 3 qadam, AI yordami
    "oqim": ("Mijoz oqimi",
             "Mijozlar kam yoki bitta kanalga bog'liq, qaysi kanal ishlashi aniq emas.",
             ["Har so'rov qayerdan kelganini yozib boring (oddiy jadval: sana, kanal, natija).",
              "Eng yaxshi ishlayotgan 1 ta kanalni toping va byudjetning ko'p qismini shunga qo'ying.",
              "Har oyda 1 ta yangi kanalni kichik sinov bilan tekshiring."],
             "AI yordamchi har bir so'rovni kanal bo'yicha avtomatik hisoblab beradi."),
    "javob": ("Javob tezligi va qamrov",
              "Mijoz yozganda tez javob olmayapti: bunday so'rovlarning bir qismi raqobatchiga ketishi mumkin.",
              ["Birinchi javob uchun maqsad qo'ying: ish vaqtida 5 daqiqa.",
               "Eng ko'p so'raladigan 10 ta savolga tayyor javoblar yozing (narx, manzil, muddat).",
               "Kechki soatlar va dam olish kunlari kim javob berishini belgilang."],
              "AI agent oddiy savollarga 24/7 javob beradi va tayyor mijozni xodimga uzatadi."),
    "konv": ("Sotuv konversiyasi",
             "So'rovlar sotuvga yetarlicha aylanmayapti yoki hisobi yo'q; 'o'ylab ko'ray' degan mijoz yo'qolyapti.",
             ["Har so'rov holatini yozing: sotildi / o'ylayapti / rad.",
              "'O'ylab ko'raman' degan mijozga 1-2 kun ichida qayta yozish qoidasini kiriting.",
              "Rad sabablarini (narx, muddat, ishonch) sanang va eng ko'pi ustida ishlang."],
             "Avtomatik eslatma va qayta aloqa mijozni yo'qotmaslikka yordam beradi."),
    "qayta": ("Qayta sotuv va mijoz bazasi",
              "Mijoz bazasi tartibsiz, eski mijozlar bilan aloqa kam: eng arzon sotuv shu yerda yo'qoladi.",
              ["Barcha mijozlarni bitta jadvalga yig'ing (ism, telefon, nima olgan, sana).",
               "Oxirgi 6 oyda sotib olganlarga shaxsiy xabar yuboring.",
               "Har oyda 1 marta yangi taklif yoki eslatma kiriting."],
              "AI mijozlarni guruhlab, har biriga mos xabarni tayyorlaydi."),
    "jarayon": ("Jarayon va xodimlar",
                "Xodimlar ishi yozilmagan yoki nazorat qilinmaydi: natija odamga bog'liq bo'lib qolgan.",
                ["Eng yaxshi sotuvchining suhbatini yozib, 5 qadamlik skript qiling.",
                 "Xodimlarga haftada 1 marta qisqa o'rgatish va tahlil belgilang.",
                 "Har bir xodimga 2-3 ta aniq ko'rsatkich bering (qo'ng'iroq, sotuv, konversiya)."],
                "AI qo'ng'iroqlarni tinglab skript bo'yicha baholaydi va kim qayerda qiynalayotganini ko'rsatadi."),
    "raqam": ("Raqamlar va nazorat",
              "Biznes his bilan boshqarilmoqda: nima ishlayotgani va nima yo'qotayotgani aniq emas.",
              ["Har kuni 3 ta raqamni yozing: so'rovlar soni, sotuvlar soni, tushum.",
               "Haftada bir marta natijani oldingi hafta bilan solishtiring.",
               "Hisobni qo'lda emas, jadval yoki dasturda yuriting."],
              "AI kunlik hisobotni avtomatik yig'ib, Telegramga yuboradi."),
}
PRIORITY = ["javob", "konv", "oqim", "qayta", "jarayon", "raqam"]  # tenglikda xizmatimizga eng mos birinchi

S = lambda area, t, o: {"k": "score", "a": area, "t": t, "o": o}
Q = [
    {"k": "profil", "t": "Biznesingiz qaysi sohada?", "o": [("🛍 Do'kon / chakana savdo", 0), ("🔧 Xizmat ko'rsatish", 0), ("🏭 Ishlab chiqarish", 0), ("🎓 Ta'lim / klinika / go'zallik", 0), ("📦 Boshqa", 0)]},
    {"k": "profil", "t": "Oylik aylanmangiz taxminan qancha?", "o": [("50 mln so'mgacha", 0), ("50–200 mln", 0), ("200 mln – 1 mlrd", 0), ("1 mlrd dan ko'p", 0)]},
    S("oqim", "Yangi mijozlar asosan qayerdan keladi?", [("Tavsiya yoki aniq bilmayman", 0), ("Bitta kanal (masalan Instagram)", 1), ("2-3 ta kanal", 2), ("Ko'p kanal, har birining natijasini bilaman", 3)]),
    S("oqim", "Reklama/marketingga oyiga byudjet ajratasizmi?", [("Yo'q", 0), ("Ba'zan, tartibsiz", 1), ("Doimiy, lekin natijasi noaniq", 2), ("Doimiy va natijasini hisoblayman", 3)]),
    S("javob", "Telegram/Instagram/qo'ng'iroqdagi so'rovga birinchi javob odatda qancha vaqtda beriladi?", [("Bir necha soat yoki ko'proq", 0), ("30-60 daqiqa", 1), ("5-30 daqiqa", 2), ("5 daqiqagacha", 3)]),
    S("javob", "O'tgan hafta nechta so'rov javobsiz qolgan?", [("Bilmayman yoki 10 dan ko'p", 0), ("5-10 ta", 1), ("1-4 ta", 2), ("Deyarli yo'q", 3)]),
    S("konv", "So'rov yozgan mijozlarning qanchasi sotib oladi?", [("Bilmayman", 0), ("10% dan kam", 1), ("10-30%", 2), ("30% dan ko'p", 3)]),
    S("konv", "Mijoz 'o'ylab ko'raman' desa, unga qayta yozilyaptimi?", [("Yo'q", 0), ("Ba'zan, xodim esiga tushsa", 1), ("Ko'pincha", 2), ("Doim, tizimli (eslatma bilan)", 3)]),
    S("qayta", "Mijozlar bazasi (ism, telefon, nima olgan) saqlanadimi?", [("Saqlanmaydi", 0), ("Telefon yoki daftarda", 1), ("Excel/jadvalda", 2), ("CRM/dasturda", 3)]),
    S("qayta", "Eski mijozlarga yangi taklif yoki eslatma yuborasizmi?", [("Yo'q", 0), ("Yiliga 1-2 marta", 1), ("Oyiga bir marta", 2), ("Muntazam, mijozga moslab", 3)]),
    S("jarayon", "Xodimlar nima deyishi va qanday sotishi yozilganmi (skript, qo'llanma)?", [("Yo'q", 0), ("Faqat og'zaki", 1), ("Qisman yozilgan", 2), ("Yozilgan va o'rgatiladi", 3)]),
    S("jarayon", "Xodimlar ishi qanday nazorat qilinadi?", [("Nazorat yo'q", 0), ("Ba'zan so'rayman", 1), ("Haftalik/oylik hisobot", 2), ("Kunlik raqamlar bilan", 3)]),
    S("raqam", "Asosiy raqamlarni (so'rov, sotuv, foyda) qachon bilib olasiz?", [("Taxminan, his bilan", 0), ("Oy oxirida", 1), ("Haftada bir", 2), ("Har kuni", 3)]),
    S("raqam", "Raqamlarni kim hisoblaydi?", [("Hech kim", 0), ("O'zim qo'lda", 1), ("Buxgalter yoki xodim", 2), ("Avtomatik dastur", 3)]),
    {"k": "text", "t": "Biznesingizdagi eng katta og'riq nima? Bir-ikki jumla yozing."},
    {"k": "ready", "t": "Topilgan muammolarni hal qilish bo'yicha qaysi gap sizga mos?", "o": [("Men qaror qabul qilaman, tayyorman", 0), ("Men qaror qilaman, avval ko'proq ma'lumot kerak", 1), ("Qarorni boshqa kishi qabul qiladi", 2), ("Hozircha faqat qiziqyapman", 3)]},
]
N = len(Q)
I_SOHA, I_AYL = 0, 1
I_TEXT = next(i for i, q in enumerate(Q) if q["k"] == "text")
I_READY = next(i for i, q in enumerate(Q) if q["k"] == "ready")

WELCOME = ("Assalomu alaykum! 👋\nMen <b>Nuqta AI</b> biznes tashxis botiman.\n\n"
           f"{N} ta qisqa savolga javob bering (taxminan 5 daqiqa). Biznesingizning kuchli tomonlari, "
           "<b>asosiy o'sish nuqtasi</b> va birinchi qadamlarni ko'rsataman.\n\n"
           "🔒 Javoblaringiz tashxis tayyorlash va siz bilan bog'lanish uchun ishlatiladi.")

# ---------- hisob-kitob ----------
def compute(ans):
    raw = {a: 0 for a in AREAS}
    for i, q in enumerate(Q):
        if q["k"] == "score":
            raw[q["a"]] += q["o"][ans[i]][1]
    area10 = {a: round(v / 6 * 10) for a, v in raw.items()}
    overall = round(sum(raw.values()) / 36 * 100)
    order = sorted(AREAS, key=lambda a: (raw[a], PRIORITY.index(a)))
    return raw, area10, overall, order

def temperature(ans):
    ready, ayl = ans[I_READY], ans[I_AYL]
    if ready == 0 and ayl >= 1: return "🔥 ISSIQ"
    if ready == 3: return "❄️ SOVUQ"
    return "🌤 ILIQ"

def bar(n): return "▓" * n + "░" * (10 - n)

def diagnosis_text(ans):
    raw, a10, overall, order = compute(ans)
    w, w2 = order[0], order[1]
    name, why, steps, ai = AREAS[w]
    lines = [f"<b>📊 Tezkor tashxis: {overall}/100</b>", ""]
    for a in AREAS:
        lines.append(f"{AREAS[a][0]}\n{bar(a10[a])} {a10[a]}/10")
    lines += ["", f"<b>🎯 Asosiy o'sish nuqtangiz: {name}</b>", why, "", "<b>Birinchi 3 qadam:</b>"]
    lines += [f"{i}. {s}" for i, s in enumerate(steps, 1)]
    lines += ["", f"<b>🤖 AI yordami:</b> {ai}", "", f"Ikkinchi e'tibor nuqtasi: <i>{AREAS[w2][0]}</i>", "",
              "ℹ️ Bu qisqa tezkor tashxis, javoblaringizga asoslangan taxminiy baho.",
              "📩 <b>Individual hisobot va 30 kunlik reja</b> 24 soat ichida shaxsan sizga yuboriladi. "
              "Savolingiz bo'lsa, shu yerga yozing."]
    return "\n".join(lines)

def save_lead(ud, user, phone, ans):
    raw, a10, overall, order = compute(ans)
    row = {"vaqt": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), "user_id": user.id,
           "username": user.username or "", "ism": user.full_name, "telefon": phone,
           "manba": ud.get("manba", ""), "soha": Q[I_SOHA]["o"][ans[I_SOHA]][0], "aylanma": Q[I_AYL]["o"][ans[I_AYL]][0],
           "umumiy_ball": overall, **{a: a10[a] for a in AREAS}, "zaif_nuqta": AREAS[order[0]][0],
           "ogriq": ans[I_TEXT], "tayyorlik": Q[I_READY]["o"][ans[I_READY]][0], "harorat": temperature(ans)}
    new = not LEADS.exists()
    with open(LEADS, "a", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=list(row))
        if new: w.writeheader()
        w.writerow(row)
    return row

def owner_text(row, user):
    e = lambda s: html.escape(s, quote=False)
    return (f"<b>🆕 Yangi lid {row['harorat']}</b>\n"
            f"<a href=\"tg://user?id={user.id}\">{e(row['ism'])}</a> {('@' + e(row['username'])) if row['username'] else ''}\n"
            f"📞 {e(str(row['telefon']))}\nSoha: {e(row['soha'])} | Aylanma: {e(row['aylanma'])}\n"
            f"Ball: {row['umumiy_ball']}/100 | Zaif nuqta: {e(row['zaif_nuqta'])}\n"
            f"Tayyorlik: {e(row['tayyorlik'])}\nOg'riq: {e(str(row['ogriq']))}"
            + (f"\nManba: {e(row['manba'])}" if row['manba'] else ""))

# ---------- Telegram qismi ----------
async def ask(context, chat_id, i):
    q = Q[i]
    head = f"<b>Savol {i + 1}/{N}</b>\n{html.escape(q['t'], quote=False)}"
    if q["k"] == "text":
        await context.bot.send_message(chat_id=chat_id, text=head + "\n\n✍️ Javobingizni yozib yuboring.", parse_mode="HTML")
    else:
        kb = InlineKeyboardMarkup([[InlineKeyboardButton(lbl, callback_data=f"a:{i}:{j}")] for j, (lbl, _) in enumerate(q["o"])])
        await context.bot.send_message(chat_id=chat_id, text=head, reply_markup=kb, parse_mode="HTML")

async def advance(context, chat_id):
    ud = context.user_data
    if ud["step"] < N:
        await ask(context, chat_id, ud["step"])
    else:
        ud["state"] = "phone"
        kb = ReplyKeyboardMarkup([[KeyboardButton("📱 Raqamimni yuborish", request_contact=True)]], resize_keyboard=True, one_time_keyboard=True)
        await context.bot.send_message(chat_id=chat_id, reply_markup=kb,
                                       text="Deyarli tayyor! Tashxis va hisobotni yuborishimiz uchun telefon raqamingizni yuboring (tugma yoki +998... yozib).")

async def finish(update, context, phone):
    ud, user, chat_id = context.user_data, update.effective_user, update.effective_chat.id
    ud["state"] = "done"
    await context.bot.send_message(chat_id=chat_id, text=diagnosis_text(ud["ans"]), parse_mode="HTML", reply_markup=ReplyKeyboardRemove())
    row = save_lead(ud, user, phone, ud["ans"])
    if OWNER:
        try: await context.bot.send_message(chat_id=OWNER, text=owner_text(row, user), parse_mode="HTML")
        except Exception as e: print("Egaga xabar yuborilmadi:", e)

async def cmd_start(update, context):
    context.user_data.clear()
    if context.args: context.user_data["manba"] = context.args[0][:40]
    kb = InlineKeyboardMarkup([[InlineKeyboardButton("✅ Boshlash", callback_data="go")]])
    await update.message.reply_text(WELCOME, reply_markup=kb, parse_mode="HTML")

async def cmd_id(update, context):
    await update.message.reply_text(f"Chat ID: {update.effective_chat.id}")

async def cmd_stat(update, context):
    if str(update.effective_chat.id) != str(OWNER): return
    rows = list(csv.DictReader(open(LEADS, encoding="utf-8-sig"))) if LEADS.exists() else []
    cnt = {}
    for r in rows: cnt[r["harorat"]] = cnt.get(r["harorat"], 0) + 1
    await update.message.reply_text(f"Lidlar: {len(rows)}\n" + "\n".join(f"{k}: {v}" for k, v in cnt.items()))

async def on_button(update, context):
    q, ud = update.callback_query, context.user_data
    await q.answer()
    d, chat_id = q.data, q.message.chat_id
    if d == "go":
        ud.update({"state": "q", "step": 0, "ans": {}})
        await ask(context, chat_id, 0); return
    if d.startswith("a:"):
        _, qi, oi = d.split(":"); qi, oi = int(qi), int(oi)
        if ud.get("state") != "q":
            await context.bot.send_message(chat_id=chat_id, text="Suhbat yangilandi. Qaytadan boshlash uchun /start bosing."); return
        if ud.get("step") != qi or Q[qi]["k"] == "text": return
        ud["ans"][qi] = oi
        await q.edit_message_text(f"<b>Savol {qi + 1}/{N}</b>\n{html.escape(Q[qi]['t'], quote=False)}\n✔ {html.escape(Q[qi]['o'][oi][0], quote=False)}", parse_mode="HTML")
        ud["step"] = qi + 1
        await advance(context, chat_id)

async def on_text(update, context):
    ud, txt, chat_id = context.user_data, update.message.text.strip(), update.effective_chat.id
    st = ud.get("state")
    if st == "q":
        i = ud["step"]
        if Q[i]["k"] != "text":
            await update.message.reply_text("Iltimos, yuqoridagi tugmalardan birini tanlang 👆"); return
        if len(txt) < 5:
            await update.message.reply_text("Iltimos, biroz batafsilroq yozing (kamida bir-ikki so'z)."); return
        ud["ans"][i] = txt[:500]; ud["step"] = i + 1
        await advance(context, chat_id)
    elif st == "phone":
        digits = re.sub(r"\D", "", txt)
        if len(digits) < 9:
            await update.message.reply_text("Raqam to'liq emas. Masalan: +998901234567, yoki pastdagi tugmadan foydalaning."); return
        await finish(update, context, "+" + digits if not txt.startswith("+") else txt)
    elif st == "done":
        if OWNER:
            u = update.effective_user
            await context.bot.send_message(chat_id=OWNER, parse_mode="HTML",
                text=f"💬 <a href=\"tg://user?id={u.id}\">{html.escape(u.full_name, quote=False)}</a>: {html.escape(txt, quote=False)}")
        await update.message.reply_text("Xabaringiz qabul qilindi. Tez orada javob beramiz.")
    else:
        await update.message.reply_text("Boshlash uchun /start bosing.")

async def on_contact(update, context):
    if context.user_data.get("state") == "phone":
        await finish(update, context, update.message.contact.phone_number)

# ---------- Kanalga avtomatik post ----------
CHANNEL = os.getenv("CHANNEL_ID", "@nuqta_ai")
SLOTS = ["09:00", "18:00"]            # Toshkent vaqti
GRACE_MIN = 30                        # kompyuter kech yoqilsa, shu daqiqagacha hali joylaydi
TASHKENT = datetime.timezone(datetime.timedelta(hours=5))
POSTS_FILE, STATE_FILE = Path("postlar.txt"), Path("post_holati.json")

def load_posts():
    if not POSTS_FILE.exists(): return []
    out = []
    for block in re.split(r"(?m)^=====\s*$", POSTS_FILE.read_text(encoding="utf-8")):
        block = block.strip()
        if not block: continue
        rasm = None
        if block.startswith("#rasm:"):
            first, _, block = block.partition("\n")
            rasm, block = first.split(":", 1)[1].strip(), block.strip()
        out.append((block, rasm))
    return out

def load_state():
    try: return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except Exception: return {"keyingi": 0, "otilgan": [], "pauza": False, "ogohlantirildi": -1}

def save_state(st):
    st["otilgan"] = st["otilgan"][-60:]
    STATE_FILE.write_text(json.dumps(st, ensure_ascii=False), encoding="utf-8")

def due_slot(now, st):
    if st.get("pauza"): return None
    for s in SLOTS:
        h, m = map(int, s.split(":"))
        start = now.replace(hour=h, minute=m, second=0, microsecond=0)
        if start <= now < start + datetime.timedelta(minutes=GRACE_MIN):
            key = f"{now:%Y-%m-%d} {s}"
            if key not in st["otilgan"]: return key
    return None

def next_slot(now):
    for d in (0, 1):
        for s in SLOTS:
            h, m = map(int, s.split(":"))
            t = (now + datetime.timedelta(days=d)).replace(hour=h, minute=m, second=0, microsecond=0)
            if t > now: return t

async def notify(bot, text):
    if OWNER:
        try: await bot.send_message(chat_id=OWNER, text=text)
        except Exception as e: print("Egaga xabar yuborilmadi:", e)
    else: print(text)

async def publish(bot, post, chat):
    text, rasm = post
    plain = lambda t: re.sub(r"<[^>]+>", "", t)
    async def send(t, **kw):
        try: return await bot.send_message(chat_id=chat, text=t, parse_mode="HTML", **kw)
        except Exception as e:
            if "parse" in str(e).lower() or "entit" in str(e).lower():
                return await bot.send_message(chat_id=chat, text=plain(t), **kw)
            raise
    if rasm and Path(rasm).exists():
        with open(rasm, "rb") as f:
            if len(text) <= 1000:
                try: await bot.send_photo(chat_id=chat, photo=f, caption=text, parse_mode="HTML")
                except Exception: f.seek(0); await bot.send_photo(chat_id=chat, photo=f, caption=plain(text))
                return
            await bot.send_photo(chat_id=chat, photo=f)
    await send(text)

async def do_post(bot, st, key):
    posts, i = load_posts(), st["keyingi"]
    st["otilgan"].append(key)
    if i >= len(posts):
        await notify(bot, "⚠️ Kanal postlari tugadi. postlar.txt ga yangi postlar qo'shing (har post ===== bilan ajratiladi).")
        save_state(st); return
    try:
        await publish(bot, posts[i], CHANNEL)
        st["keyingi"] = i + 1
        left = len(posts) - (i + 1)
        msg = f"✅ Kanalga {i + 1}-post joylandi ({key}). Qolgan postlar: {left}"
        if left <= 3 and st.get("ogohlantirildi") != i:
            st["ogohlantirildi"] = i; msg += "\n⚠️ Postlar tugab qolyapti, yangilarini qo'shing."
        await notify(bot, msg)
    except Exception as e:
        await notify(bot, f"❌ {i + 1}-post joylanmadi: {e}\nBot kanalda admin va 'Post messages' ruxsati borligini tekshiring. Qo'lda: /post_hozir")
    save_state(st)

async def tick(bot, now=None):
    now = now or datetime.datetime.now(TASHKENT)
    st = load_state()
    key = due_slot(now, st)
    if key: await do_post(bot, st, key)

async def planner(app):
    while True:
        try: await tick(app.bot)
        except Exception as e: print("Rejalovchi xatosi:", e)
        await asyncio.sleep(20)

async def on_start(app):
    app.bot_data["planner"] = asyncio.create_task(planner(app))
    print(f"Kanal avto-post yoqilgan: {CHANNEL}, vaqtlar {', '.join(SLOTS)} (Toshkent)")

def is_owner(update): return bool(OWNER) and str(update.effective_chat.id) == str(OWNER)

async def cmd_post_korish(update, context):
    if not is_owner(update): return
    posts, i = load_posts(), load_state()["keyingi"]
    if i >= len(posts): await update.message.reply_text("Postlar tugagan."); return
    await update.message.reply_text(f"👀 Keyingi post ({i + 1}-post) ko'rinishi:")
    await publish(context.bot, posts[i], update.effective_chat.id)

async def cmd_post_hozir(update, context):
    if not is_owner(update): return
    await do_post(context.bot, load_state(), f"qo'lda {datetime.datetime.now(TASHKENT):%Y-%m-%d %H:%M:%S}")

async def cmd_post_pauza(update, context):
    if not is_owner(update): return
    st = load_state(); st["pauza"] = True; save_state(st)
    await update.message.reply_text("⏸ Avto-post to'xtatildi. Davom ettirish: /post_davom")

async def cmd_post_davom(update, context):
    if not is_owner(update): return
    st = load_state(); st["pauza"] = False; save_state(st)
    await update.message.reply_text("▶️ Avto-post davom etadi.")

async def cmd_post_holat(update, context):
    if not is_owner(update): return
    st, posts = load_state(), load_posts()
    nxt = next_slot(datetime.datetime.now(TASHKENT))
    await update.message.reply_text(f"Kanal: {CHANNEL}\nJoylangan: {st['keyingi']} | Qolgan: {max(0, len(posts) - st['keyingi'])}\n"
                                    f"Keyingi vaqt: {nxt:%d.%m %H:%M}\nHolat: {'⏸ pauza' if st.get('pauza') else '▶️ faol'}")

def main():
    if not BOT_TOKEN:
        raise SystemExit("BOT_TOKEN o'rnatilmagan. BOT_BOSHLASH.md ni ko'ring.")
    app = Application.builder().token(BOT_TOKEN).post_init(on_start).connect_timeout(30).read_timeout(30).write_timeout(30).pool_timeout(30).get_updates_connect_timeout(30).get_updates_read_timeout(30).build()
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("id", cmd_id))
    app.add_handler(CommandHandler("stat", cmd_stat))
    for n, f in [("post_korish", cmd_post_korish), ("post_hozir", cmd_post_hozir), ("post_pauza", cmd_post_pauza), ("post_davom", cmd_post_davom), ("post_holat", cmd_post_holat)]:
        app.add_handler(CommandHandler(n, f))
    app.add_handler(CallbackQueryHandler(on_button))
    app.add_handler(MessageHandler(filters.CONTACT, on_contact))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, on_text))
    print("Bot ishga tushdi. To'xtatish: Ctrl+C")
    app.run_polling()

if __name__ == "__main__":
    main()
