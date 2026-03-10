"""
Telegram Gift Sender
Требует: pip install pyrofork tgcrypto-pyrofork qrcode pillow
"""

import asyncio
import sys
import os
import json
import msvcrt
import threading

CONFIG_FILE = "config.json"
MAX_MSG_LEN = 128

GIFTS = [
    {"name": "Новогодняя елка",    "emoji": "🎄", "stars": 50, "id": 5922558454332916696},
    {"name": "Новогодний мишка",   "emoji": "🐻", "stars": 50, "id": 5956217000635139069},
    {"name": "Сердце 14 февраля",  "emoji": "❤️", "stars": 50, "id": 5801108895304779062},
    {"name": "Мишка 14 февраля",   "emoji": "🐻", "stars": 50, "id": 5800655655995968830},
    {"name": "Мишка 8 марта",      "emoji": "🐻", "stars": 50, "id": 5866352046986232958},
    {"name": "Кастомный ID",       "emoji": "✏️", "stars": None, "id": None},
]


# ══════════════════════════════════════════════
#  Конфиг
# ══════════════════════════════════════════════

def load_config() -> dict:
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def save_config(data: dict):
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"⚠️  Не удалось сохранить настройки: {e}")


# ══════════════════════════════════════════════
#  Посимвольный ввод с живым счётчиком
# ══════════════════════════════════════════════

def input_with_counter(prompt: str, max_len: int) -> str:
    text = []

    def redraw():
        remaining = max_len - len(text)
        line = f"\r{prompt}{''.join(text)}  [{remaining}/{max_len}]"
        # Затираем остаток строки пробелами (на случай если текст стал короче)
        sys.stdout.write(line + "          \r" + line)
        sys.stdout.flush()

    redraw()
    while True:
        # Читаем все доступные символы разом (обрабатывает вставку через Ctrl+V)
        ch = msvcrt.getwch()
        if ch in ("\r", "\n"):
            print()
            break
        elif ch == "\x03":
            print()
            raise KeyboardInterrupt
        elif ch in ("\x08", "\x7f"):
            if text:
                text.pop()
                redraw()
        elif ch in ("\x00", "\xe0"):
            msvcrt.getwch()  # игнорируем стрелки и т.п.
        else:
            # Собираем все символы которые уже есть в буфере (вставка = много символов сразу)
            chars = [ch]
            while msvcrt.kbhit():
                next_ch = msvcrt.getwch()
                if next_ch in ("\r", "\n", "\x03", "\x00", "\xe0"):
                    # Если встретили Enter среди вставленного — заканчиваем
                    if next_ch in ("\r", "\n"):
                        for c in chars:
                            if len(text) < max_len:
                                text.append(c)
                        print()
                        return "".join(text)
                    break
                chars.append(next_ch)

            # Добавляем все символы разом, не превышая лимит
            for c in chars:
                if len(text) < max_len:
                    text.append(c)

            redraw()

            if len(text) >= max_len:
                sys.stdout.write(f"  [0/{max_len}] ⚠️ лимит!")
                sys.stdout.flush()

    return "".join(text)


# ══════════════════════════════════════════════
#  QR-окно (с поддержкой обновления токена)
# ══════════════════════════════════════════════

def make_qr_image(url: str):
    """Создаёт PIL-изображение QR-кода."""
    import qrcode
    qr = qrcode.QRCode(box_size=8, border=3)
    qr.add_data(url)
    qr.make(fit=True)
    return qr.make_image(fill_color="black", back_color="white").convert("RGB")


def show_qr_window(url_holder: dict, stop_event: threading.Event):
    """
    Показывает окно с QR. url_holder["url"] может обновляться извне —
    окно перерисует QR автоматически. Закрывается когда stop_event установлен.
    """
    try:
        from PIL import ImageTk
        import tkinter as tk

        root = tk.Tk()
        root.title("📱 Отсканируйте QR-код в Telegram")
        root.resizable(False, False)

        img = make_qr_image(url_holder["url"])
        tk_img = ImageTk.PhotoImage(img)

        label_img = tk.Label(root, image=tk_img)
        label_img.pack(padx=10, pady=(10, 5))

        label_txt = tk.Label(
            root,
            text="Telegram → Настройки → Устройства → Подключить устройство",
            font=("Segoe UI", 10),
            justify="center",
            fg="#333333"
        )
        label_txt.pack(padx=10, pady=(0, 10))

        last_url = url_holder["url"]

        def tick():
            nonlocal last_url, tk_img
            if stop_event.is_set():
                root.destroy()
                return
            # Если URL обновился — перерисовываем QR
            if url_holder["url"] != last_url:
                last_url = url_holder["url"]
                new_img = make_qr_image(last_url)
                tk_img = ImageTk.PhotoImage(new_img)
                label_img.config(image=tk_img)
                label_img.image = tk_img
            root.after(500, tick)

        root.after(500, tick)
        root.mainloop()
    except Exception as e:
        print(f"\n⚠️  Не удалось открыть QR-окно: {e}")


# ══════════════════════════════════════════════
#  Авторизация через QR
# ══════════════════════════════════════════════

async def authorize_qr(app):
    """Авторизация через QR с отображением в отдельном окне."""
    import base64
    from pyrogram.raw import functions as raw_fn, types as raw_t
    from pyrogram.errors import SessionPasswordNeeded

    stop_event = threading.Event()

    print("\n📱 Авторизация через QR-код...")
    print("   Открывается окно с QR — отсканируйте его в Telegram:")
    print("   Настройки → Устройства → Подключить устройство")
    print("   ⏳ Ожидание сканирования...")

    # Первый токен
    r = await app.invoke(raw_fn.auth.ExportLoginToken(
        api_id=app.api_id,
        api_hash=app.api_hash,
        except_ids=[]
    ))
    token_b64 = base64.urlsafe_b64encode(r.token).decode().rstrip("=")
    url_holder = {"url": f"tg://login?token={token_b64}"}

    # Запускаем окно — передаём словарь, чтобы обновлять URL внутри
    qr_thread = threading.Thread(target=show_qr_window, args=(url_holder, stop_event), daemon=True)
    qr_thread.start()

    # Ждём авторизации до 3 минут, обновляя токен каждые 20 сек
    deadline = asyncio.get_event_loop().time() + 180
    while asyncio.get_event_loop().time() < deadline:
        await asyncio.sleep(20)
        try:
            r2 = await app.invoke(raw_fn.auth.ExportLoginToken(
                api_id=app.api_id,
                api_hash=app.api_hash,
                except_ids=[]
            ))
            if not isinstance(r2, raw_t.auth.LoginToken):
                # Авторизация прошла
                stop_event.set()
                return True
            # Токен обновился — обновляем URL в словаре, окно само перерисует QR
            if r2.token != r.token:
                token_b64 = base64.urlsafe_b64encode(r2.token).decode().rstrip("=")
                url_holder["url"] = f"tg://login?token={token_b64}"
                r = r2
        except SessionPasswordNeeded:
            stop_event.set()
            print("\n🔐 Требуется пароль двухфакторной аутентификации.")
            from pyrogram.utils import compute_password_check
            pwd_info = await app.invoke(raw_fn.account.GetPassword())
            pwd = input("🔑 Пароль 2FA: ").strip()
            await app.invoke(raw_fn.auth.CheckPassword(
                password=compute_password_check(pwd_info, pwd)
            ))
            return True
        except Exception as e:
            err = str(e)
            if "SESSION_PASSWORD_NEEDED" in err:
                stop_event.set()
                print("\n🔐 Требуется пароль двухфакторной аутентификации.")
                pwd = input("🔑 Пароль 2FA: ").strip()
                await app.check_password(pwd)
                return True
            stop_event.set()
            return True

    stop_event.set()
    print("\n❌ Время ожидания QR истекло. Попробуйте снова.")
    return False


# ══════════════════════════════════════════════
#  Меню выбора подарка
# ══════════════════════════════════════════════

def choose_gift() -> int:
    print()
    print("=" * 60)
    print("📋 ВЫБЕРИТЕ ПОДАРОК")
    print("-" * 60)
    for i, g in enumerate(GIFTS, 1):
        stars = f"⭐ {g['stars']}" if g["stars"] else "   ?"
        print(f"   {i}) {g['emoji']} {g['name']}  {stars}")
    print("-" * 60)

    while True:
        s = input(f"🎁 Номер подарка (1–{len(GIFTS)}): ").strip()
        if s.isdigit() and 1 <= int(s) <= len(GIFTS):
            gift = GIFTS[int(s) - 1]
            if gift["id"] is None:
                while True:
                    cid = input("✏️  Введите Gift ID: ").strip()
                    if cid.isdigit():
                        return int(cid)
                    print("❌ ID должен содержать только цифры.")
            else:
                print(f"   ✅ Выбран: {gift['emoji']} {gift['name']}")
                return gift["id"]
        print(f"❌ Введите число от 1 до {len(GIFTS)}.")


# ══════════════════════════════════════════════
#  Ввод учётных данных
# ══════════════════════════════════════════════

def get_credentials():
    config = load_config()

    print("=" * 60)
    print("🎁  TELEGRAM GIFT SENDER")
    print("=" * 60)

    if config:
        print()
        print("💾 Найдены сохранённые настройки:")
        print(f"   API_ID:  {config.get('api_id', '?')}")
        print(f"   Сессия:  {config.get('session_name', '?')}.session")
        print("-" * 60)
        ans = input("♻️  Использовать их? (Enter = да  /  no = заново): ").strip().lower()
        if ans not in ("no", "n", "нет", "н"):
            print("✅ Используются сохранённые настройки.")
            return config["api_id"], config["api_hash"], config.get("session_name", "gift_session")

    print()
    print("📋 ШАГ 1: TELEGRAM API")
    print("-" * 60)
    print("ℹ️  Получить API_ID и API_HASH на my.telegram.org:")
    print("   1. Войдите своим номером телефона")
    print("   2. Нажмите 'API development tools'")
    print("   3. Создайте приложение (название любое)")
    print("   4. Скопируйте App api_id и App api_hash")
    print("-" * 60)

    while True:
        s = input("🔑 API_ID (только цифры): ").strip()
        if s.isdigit():
            api_id = int(s)
            break
        print("❌ Только цифры, попробуйте снова.")

    while True:
        api_hash = input("🔑 API_HASH: ").strip()
        if len(api_hash) >= 10:
            break
        print("❌ Слишком короткий, проверьте и введите снова.")

    print()
    print("📋 ШАГ 2: ИМЯ СЕССИИ")
    print("-" * 60)
    print("ℹ️  Название файла сессии. Enter — стандартное.")
    print("-" * 60)
    session_name = input("💾 Имя сессии (Enter = 'gift_session'): ").strip() or "gift_session"
    print(f"   ✅ Сессия: {session_name}.session")

    save_config({"api_id": api_id, "api_hash": api_hash, "session_name": session_name})
    print("💾 Настройки сохранены в config.json")

    return api_id, api_hash, session_name


# ══════════════════════════════════════════════
#  Отправка подарка
# ══════════════════════════════════════════════

async def send_gift(api_id: int, api_hash: str, session_name: str):
    from pyrogram import Client
    from pyrogram.raw import functions, types as raw_types

    workdir = os.path.dirname(os.path.abspath(sys.argv[0]))
    session_path = os.path.join(workdir, session_name + ".session")
    already_authorized = os.path.exists(session_path)

    print()
    print("=" * 60)
    print("📡 ВХОД В АККАУНТ")
    print("=" * 60)

    # Если сессии нет — спрашиваем способ входа
    login_method = "phone"
    if not already_authorized:
        print()
        print("   Вход в аккаунт")
        print("   1) Войти по номеру телефона")
        print("   2) Войти по QR")
        print("-" * 60)
        while True:
            m = input("   Выберите (1 или 2): ").strip()
            if m in ("1", "2"):
                login_method = "phone" if m == "1" else "qr"
                break
            print("   ❌ Введите 1 или 2.")

    # Перехватываем встроенный input() Pyrogram чтобы показать своё меню
    # вместо стандартного "Enter phone number or bot token: qrcode"
    import builtins
    _original_input = builtins.input
    _login_choice = {"method": login_method}  # передаём выбор внутрь closure

    def _patched_input(prompt=""):
        # Pyrogram спрашивает номер/токен — именно здесь показываем наше меню
        if "phone number" in prompt.lower() or "bot token" in prompt.lower():
            if _login_choice["method"] == "qr":
                # Говорим Pyrogram использовать qrcode — он сам откроет QR-флоу
                # но мы перехватим его ниже через authorize_qr
                return "qrcode"
            else:
                print()
                print("ℹ️  Введите номер телефона в формате +79001234567")
                print("   Код подтверждения придёт в приложение Telegram.")
                print("-" * 60)
                return _original_input("📱 Номер телефона: ").strip()
        # Перехватываем запрос кода подтверждения
        if "code" in prompt.lower():
            return _original_input("🔑 Код из Telegram: ").strip()
        # Перехватываем запрос 2FA пароля
        if "password" in prompt.lower():
            return _original_input("🔐 Пароль 2FA: ").strip()
        return _original_input(prompt)

    builtins.input = _patched_input

    app = Client(
        name=session_name,
        api_id=api_id,
        api_hash=api_hash,
        workdir=workdir,
    )

    if login_method == "qr" and not already_authorized:
        # Запускаем клиент без авторизации, авторизуемся вручную через QR
        builtins.input = _original_input  # восстанавливаем до connect
        await app.connect()
        try:
            ok = await authorize_qr(app)
            if not ok:
                await app.disconnect()
                return
            await app.storage.save()
        except Exception as e:
            print(f"\n❌ Ошибка QR-авторизации: {e}")
            await app.disconnect()
            return
        print("\n✅ QR-авторизация успешна!")
        me = await app.get_me()
    else:
        await app.start()
        builtins.input = _original_input  # восстанавливаем после старта
        me = await app.get_me()

    print(f"\n✅ Вы вошли как: {me.first_name}", end="")
    if me.last_name:
        print(f" {me.last_name}", end="")
    if me.username:
        print(f" (@{me.username})")
    else:
        print()

    try:
        # --- ВЫБОР ПОДАРКА ---
        gift_id = choose_gift()

        # --- ПОЛУЧАТЕЛЬ ---
        print()
        print("=" * 60)
        print("📋 ПОЛУЧАТЕЛЬ")
        print("-" * 60)
        print("ℹ️  Username без @ или номер телефона (+79001234567).")
        print("-" * 60)
        recipient = input("👤 Получатель: ").strip().lstrip("@")

        print(f"\n🔍 Поиск: {recipient} ...")
        try:
            user = await app.get_users(recipient)
            print(f"✅ Найден: {user.first_name}", end="")
            if user.last_name:
                print(f" {user.last_name}", end="")
            if user.username:
                print(f" (@{user.username})")
            else:
                print()
        except Exception as e:
            print(f"❌ Пользователь '{recipient}' не найден: {e}")
            print("   Проверьте username или сначала напишите ему в Telegram.")
            return

        # --- СООБЩЕНИЕ с счётчиком ---
        print()
        print("=" * 60)
        print("📋 СООБЩЕНИЕ К ПОДАРКУ  (необязательно, Enter — пропустить)")
        print("-" * 60)
        message_text = input_with_counter("💌 Сообщение: ", MAX_MSG_LEN)

        # --- АНОНИМНОСТЬ ---
        print()
        print("=" * 60)
        print("📋 АНОНИМНОСТЬ")
        print("-" * 60)
        print("ℹ️  Скрыть своё имя у получателя?")
        print("-" * 60)
        hide_name = input("🕵️  Анонимно? (yes/no, Enter = нет): ").strip().lower() in ("yes", "y", "да", "д")

        # --- ИТОГ ---
        gift_label = next((f"{g['emoji']} {g['name']}" for g in GIFTS if g["id"] == gift_id), f"ID {gift_id}")
        print()
        print("=" * 60)
        print("✅ ПРОВЕРЬТЕ ДАННЫЕ")
        print("-" * 60)
        print(f"🎁 Подарок:    {gift_label}")
        print(f"📤 Получатель: {user.first_name}", end="")
        if user.last_name:
            print(f" {user.last_name}", end="")
        if user.username:
            print(f" (@{user.username})")
        else:
            print()
        print(f"💌 Сообщение:  {message_text or '(без сообщения)'}")
        print(f"🕵️  Анонимно:   {'Да' if hide_name else 'Нет'}")
        print("-" * 60)

        if input("\n❓ Отправить? (yes/no): ").strip().lower() not in ("yes", "y", "да", "д"):
            print("\n❌ Отменено.")
            return

        print("\n🎁 Отправка подарка...")

        peer = await app.resolve_peer(user.id)
        message_obj = raw_types.TextWithEntities(text=message_text, entities=[]) if message_text else None

        invoice = raw_types.InputInvoiceStarGift(
            peer=peer,
            gift_id=gift_id,
            hide_name=hide_name,
            message=message_obj,
        )

        payment_form = await app.invoke(
            functions.payments.GetPaymentForm(invoice=invoice)
        )

        if hasattr(payment_form, "invoice") and payment_form.invoice.prices:
            stars = payment_form.invoice.prices[0].amount
            print(f"💰 Стоимость: ⭐ {stars} Stars")

        await app.invoke(
            functions.payments.SendStarsForm(
                form_id=payment_form.form_id,
                invoice=invoice,
            )
        )

        print(f"\n✅ ПОДАРОК ОТПРАВЛЕН! 🎉")
        print(f"🎁 Доставлен пользователю {user.first_name}")

    except Exception as e:
        msg = str(e)
        print(f"\n❌ Ошибка: {msg}")
        if "BALANCE_TOO_LOW" in msg:
            print("💡 Недостаточно Stars. Telegram → Настройки → Telegram Stars")
        elif "PEER_ID_INVALID" in msg:
            print("💡 Неверный ID. Сначала напишите этому пользователю в Telegram.")
        elif "GIFT_SEND_DISALLOWED" in msg:
            print("💡 Пользователь запретил получение подарков.")
        elif "STARGIFT_USAGE_LIMITED" in msg:
            print("💡 Этот подарок закончился в магазине.")

    finally:
        try:
            await app.stop()
        except Exception:
            try:
                await app.disconnect()
            except Exception:
                pass
        print("\n🔌 Отключено.")
        print("=" * 60)


# ══════════════════════════════════════════════
#  Точка входа
# ══════════════════════════════════════════════

async def main():
    if sys.platform.startswith("win"):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    print("\n🚀 Добро пожаловать в Telegram Gift Sender!\n")
    api_id, api_hash, session_name = get_credentials()

    while True:
        await send_gift(api_id, api_hash, session_name)
        print()
        if input("🔄 Отправить ещё? (yes/no): ").strip().lower() not in ("yes", "y", "да", "д"):
            print("\n👋 До свидания!")
            break
        print()


if __name__ == "__main__":
    asyncio.run(main())