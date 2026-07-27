import asyncio
import sys
import os
import json
import msvcrt


APP_NAME      = "TelegramGiftSender"
APPDATA_DIR   = os.path.join(os.environ.get("APPDATA", os.path.expanduser("~")), APP_NAME)
CONFIG_FILE   = os.path.join(APPDATA_DIR, "config.json")
MAX_MSG_LEN   = 128

BACK_TOKENS = {"0", "back", "назад", "b", "н"}

os.makedirs(APPDATA_DIR, exist_ok=True)


def is_back(s: str) -> bool:
    return s.strip().lower() in BACK_TOKENS


STRINGS = {
    "ru": {
        "welcome":           "🚀 Добро пожаловать в Telegram Gift Sender!",
        "choose_lang":       "🌐 Язык / Language:\n   1) Русский\n   2) English\n",
        "lang_prompt":       "Выберите (1/2): ",
        "gifts_title":       "📋 ВЫБЕРИТЕ ПОДАРОК",
        "gifts_custom_id":   "✏️  Введите Gift ID (0 — назад): ",
        "gifts_invalid_id":  "❌ ID должен содержать только цифры.",
        "gifts_prompt":      "🎁 Номер подарка (1–{n}, 0/Enter — отмена): ",
        "gifts_invalid":     "❌ Введите число от 1 до {n}.",
        "gifts_selected":    "   ✅ Выбран: {emoji} {name}",
        "login_title":       "📡 ВХОД В АККАУНТ",
        "login_method":      "   Вход в аккаунт\n   1) По номеру телефона\n   2) По QR-коду\n",
        "login_method_p":    "   Выберите (1 или 2): ",
        "login_method_err":  "   ❌ Введите 1 или 2.",
        "phone_hint":        "ℹ️  Введите номер телефона в формате +79001234567",
        "phone_prompt":      "📱 Номер телефона: ",
        "code_prompt":       "🔑 Код из Telegram: ",
        "password_prompt":   "🔐 Пароль 2FA: ",
        "logged_as":         "✅ Вы вошли как: ",
        "recipient_title":   "📋 ПОЛУЧАТЕЛЬ",
        "recipient_hint":    "ℹ️  Username без @ или номер телефона (+79001234567).",
        "recipient_back":    "↩️  Enter или 0 — назад, к выбору подарка.",
        "recipient_prompt":  "👤 Получатель: ",
        "recipient_search":  "🔍 Поиск: {r} ...",
        "recipient_found":   "✅ Найден: ",
        "recipient_tip":     "   Проверьте username или сначала напишите ему в Telegram.",
        "msg_title":         "📋 СООБЩЕНИЕ К ПОДАРКУ  (Enter — пропустить, 0 — назад)",
        "msg_prompt":        "💌 Сообщение: ",
        "anon_title":        "📋 АНОНИМНОСТЬ",
        "anon_hint":         "ℹ️  Скрыть своё имя у получателя?",
        "anon_prompt":       "🕵️  Анонимно? (yes/no, Enter = нет, 0 = назад): ",
        "confirm_title":     "✅ ПРОВЕРЬТЕ ДАННЫЕ",
        "confirm_gift":      "🎁 Подарок:    ",
        "confirm_rcpt":      "📤 Получатель: ",
        "confirm_msg":       "💌 Сообщение:  ",
        "confirm_anon":      "🕵️  Анонимно:   ",
        "confirm_yes":       "Да",
        "confirm_no":        "Нет",
        "confirm_no_msg":    "(без сообщения)",
        "confirm_prompt":    "\n❓ Отправить? (yes/no, 0 — назад): ",
        "confirm_cancel":    "\n❌ Отменено.",
        "order_cancelled":   "\n↩️  Возврат в главное меню.",
        "sending":           "\n🎁 Отправка подарка...",
        "cost":              "💰 Стоимость: ⭐ {stars} Stars",
        "success":           "\n✅ ПОДАРОК ОТПРАВЛЕН! 🎉",
        "delivered":         "🎁 Доставлен пользователю {name}",
        "err_unknown":       "Что-то пошло не так.",
        "disconnected":      "\n🔌 Отключено.",
        "again_prompt":      "🔄 Отправить ещё? (yes/no): ",
        "goodbye":           "\n👋 До свидания!",
        "qr_opening":        "\n📱 Авторизация через QR-код...",
        "qr_hint":           "   Откройте Telegram → Настройки → Устройства → Подключить устройство",
        "qr_waiting":        "   ⏳ Ожидание сканирования...",
        "qr_expired":        "\n❌ Время ожидания QR истекло. Попробуйте снова.",
        "qr_ok":             "\n✅ QR-авторизация успешна!",
        "qr_2fa":            "\n🔐 Требуется пароль двухфакторной аутентификации.",
        "qr_2fa_p":          "🔑 Пароль 2FA: ",
        "session_reset":     "♻️  Старая сессия удалена. Нужно войти заново.",
        "login_retry":       "🔁 Пробуем ещё раз...",
        "login_failed":      "\n❌ Не удалось войти в аккаунт. Перезапустите программу и попробуйте снова.",
        "api_title":         "📋 ШАГ 1: TELEGRAM API",
        "api_hint":          (
            "ℹ️  Получить API_ID и API_HASH на my.telegram.org:\n"
            "   1. Войдите своим номером телефона\n"
            "   2. Нажмите 'API development tools'\n"
            "   3. Создайте приложение (название любое)\n"
            "   4. Скопируйте App api_id и App api_hash"
        ),
        "api_id_prompt":     "🔑 API_ID (только цифры): ",
        "api_id_err":        "❌ Только цифры, попробуйте снова.",
        "api_hash_prompt":   "🔑 API_HASH: ",
        "api_hash_err":      "❌ Слишком короткий, проверьте и введите снова.",
        "session_prompt":    "💾 Имя сессии (Enter = 'gift_session'): ",
        "session_ok":        "   ✅ Сессия: {name}.session",
        "config_saved":      "💾 Настройки сохранены.",
        "yes_values":        ("yes", "y", "да", "д"),
        "errors": {
            "UsernameInvalid":      "Такого username не существует.",
            "UsernameNotOccupied":  "Username свободен — такого пользователя нет.",
            "PeerIdInvalid":        "Telegram пока не знает этого пользователя. Сначала напишите ему хотя бы одно сообщение в Telegram.",
            "BalanceTooLow":        "Недостаточно Telegram Stars на балансе. Пополнить: Telegram → Настройки → Telegram Stars.",
            "StargiftUsageLimited": "Этот подарок закончился в магазине.",
            "GiftSendDisallowed":   "Получатель запретил присылать ему подарки.",
            "AuthKeyUnregistered":  "Сессия входа устарела или была отозвана — нужно войти заново.",
            "FloodWait":            "Telegram временно ограничил запросы. Подождите немного и попробуйте снова.",
            "PhoneNumberInvalid":   "Неверный формат номера телефона.",
            "PhoneCodeInvalid":     "Неверный код из Telegram.",
            "PasswordHashInvalid":  "Неверный пароль двухфакторной аутентификации.",
            "StargiftInvalid":      "Такого подарка не существует — проверьте Gift ID.",
        },
        "error_substrings": [
            ("USERNAME_INVALID",       "Такого username не существует."),
            ("USERNAME_NOT_OCCUPIED",  "Username свободен — такого пользователя нет."),
            ("PEER_ID_INVALID",        "Telegram пока не знает этого пользователя. Сначала напишите ему хотя бы одно сообщение в Telegram."),
            ("BALANCE_TOO_LOW",        "Недостаточно Telegram Stars на балансе. Пополнить: Telegram → Настройки → Telegram Stars."),
            ("STARGIFT_USAGE_LIMITED", "Этот подарок закончился в магазине."),
            ("GIFT_SEND_DISALLOWED",   "Получатель запретил присылать ему подарки."),
            ("AUTH_KEY_UNREGISTERED",  "Сессия входа устарела или была отозвана — нужно войти заново."),
            ("FLOOD_WAIT",             "Telegram временно ограничил запросы. Подождите немного и попробуйте снова."),
            ("STARGIFT_ID_INVALID",    "Такого подарка не существует — проверьте Gift ID."),
            ("GIFT_ID_INVALID",        "Такого подарка не существует — проверьте Gift ID."),
        ],
    },
    "en": {
        "welcome":           "🚀 Welcome to Telegram Gift Sender!",
        "choose_lang":       "🌐 Язык / Language:\n   1) Русский\n   2) English\n",
        "lang_prompt":       "Choose (1/2): ",
        "gifts_title":       "📋 CHOOSE A GIFT",
        "gifts_custom_id":   "✏️  Enter Gift ID (0 — back): ",
        "gifts_invalid_id":  "❌ ID must contain digits only.",
        "gifts_prompt":      "🎁 Gift number (1–{n}, 0/Enter — cancel): ",
        "gifts_invalid":     "❌ Enter a number from 1 to {n}.",
        "gifts_selected":    "   ✅ Selected: {emoji} {name}",
        "login_title":       "📡 ACCOUNT LOGIN",
        "login_method":      "   Login to account\n   1) Phone number\n   2) QR code\n",
        "login_method_p":    "   Choose (1 or 2): ",
        "login_method_err":  "   ❌ Enter 1 or 2.",
        "phone_hint":        "ℹ️  Enter phone number in format +12345678901",
        "phone_prompt":      "📱 Phone number: ",
        "code_prompt":       "🔑 Telegram code: ",
        "password_prompt":   "🔐 2FA password: ",
        "logged_as":         "✅ Logged in as: ",
        "recipient_title":   "📋 RECIPIENT",
        "recipient_hint":    "ℹ️  Username without @ or phone number (+12345678901).",
        "recipient_back":    "↩️  Enter or 0 — back to gift selection.",
        "recipient_prompt":  "👤 Recipient: ",
        "recipient_search":  "🔍 Searching: {r} ...",
        "recipient_found":   "✅ Found: ",
        "recipient_tip":     "   Check the username or message them on Telegram first.",
        "msg_title":         "📋 GIFT MESSAGE  (Enter — skip, 0 — back)",
        "msg_prompt":        "💌 Message: ",
        "anon_title":        "📋 ANONYMITY",
        "anon_hint":         "ℹ️  Hide your name from the recipient?",
        "anon_prompt":       "🕵️  Anonymous? (yes/no, Enter = no, 0 = back): ",
        "confirm_title":     "✅ REVIEW YOUR ORDER",
        "confirm_gift":      "🎁 Gift:       ",
        "confirm_rcpt":      "📤 Recipient:  ",
        "confirm_msg":       "💌 Message:    ",
        "confirm_anon":      "🕵️  Anonymous:  ",
        "confirm_yes":       "Yes",
        "confirm_no":        "No",
        "confirm_no_msg":    "(no message)",
        "confirm_prompt":    "\n❓ Send? (yes/no, 0 — back): ",
        "confirm_cancel":    "\n❌ Cancelled.",
        "order_cancelled":   "\n↩️  Back to main menu.",
        "sending":           "\n🎁 Sending gift...",
        "cost":              "💰 Cost: ⭐ {stars} Stars",
        "success":           "\n✅ GIFT SENT! 🎉",
        "delivered":         "🎁 Delivered to {name}",
        "err_unknown":       "Something went wrong.",
        "disconnected":      "\n🔌 Disconnected.",
        "again_prompt":      "🔄 Send another? (yes/no): ",
        "goodbye":           "\n👋 Goodbye!",
        "qr_opening":        "\n📱 QR code authorization...",
        "qr_hint":           "   Open Telegram → Settings → Devices → Link Desktop Device",
        "qr_waiting":        "   ⏳ Waiting for scan...",
        "qr_expired":        "\n❌ QR code timed out. Please try again.",
        "qr_ok":             "\n✅ QR authorization successful!",
        "qr_2fa":            "\n🔐 Two-factor authentication required.",
        "qr_2fa_p":          "🔑 2FA password: ",
        "session_reset":     "♻️  Old session removed. You need to log in again.",
        "login_retry":       "🔁 Trying again...",
        "login_failed":      "\n❌ Could not log in. Restart the program and try again.",
        "api_title":         "📋 STEP 1: TELEGRAM API",
        "api_hint":          (
            "ℹ️  Get API_ID and API_HASH at my.telegram.org:\n"
            "   1. Log in with your phone number\n"
            "   2. Click 'API development tools'\n"
            "   3. Create an application (any name)\n"
            "   4. Copy App api_id and App api_hash"
        ),
        "api_id_prompt":     "🔑 API_ID (digits only): ",
        "api_id_err":        "❌ Digits only, please try again.",
        "api_hash_prompt":   "🔑 API_HASH: ",
        "api_hash_err":      "❌ Too short — check and re-enter.",
        "session_prompt":    "💾 Session name (Enter = 'gift_session'): ",
        "session_ok":        "   ✅ Session: {name}.session",
        "config_saved":      "💾 Settings saved.",
        "yes_values":        ("yes", "y"),
        "errors": {
            "UsernameInvalid":      "That username doesn't exist.",
            "UsernameNotOccupied":  "That username is free — no such user.",
            "PeerIdInvalid":        "Telegram doesn't know this user yet. Message them at least once on Telegram first.",
            "BalanceTooLow":        "Not enough Telegram Stars. Top up: Telegram → Settings → Telegram Stars.",
            "StargiftUsageLimited": "This gift is sold out.",
            "GiftSendDisallowed":   "The recipient has disabled gifts.",
            "AuthKeyUnregistered":  "The saved login session expired or was revoked — need to log in again.",
            "FloodWait":            "Telegram is temporarily rate-limiting requests. Wait a bit and try again.",
            "PhoneNumberInvalid":   "Invalid phone number format.",
            "PhoneCodeInvalid":     "Invalid Telegram code.",
            "PasswordHashInvalid":  "Invalid 2FA password.",
            "StargiftInvalid":      "That gift doesn't exist — check the Gift ID.",
        },
        "error_substrings": [
            ("USERNAME_INVALID",       "That username doesn't exist."),
            ("USERNAME_NOT_OCCUPIED",  "That username is free — no such user."),
            ("PEER_ID_INVALID",        "Telegram doesn't know this user yet. Message them at least once on Telegram first."),
            ("BALANCE_TOO_LOW",        "Not enough Telegram Stars. Top up: Telegram → Settings → Telegram Stars."),
            ("STARGIFT_USAGE_LIMITED", "This gift is sold out."),
            ("GIFT_SEND_DISALLOWED",   "The recipient has disabled gifts."),
            ("AUTH_KEY_UNREGISTERED",  "The saved login session expired or was revoked — need to log in again."),
            ("FLOOD_WAIT",             "Telegram is temporarily rate-limiting requests. Wait a bit and try again."),
            ("STARGIFT_ID_INVALID",    "That gift doesn't exist — check the Gift ID."),
            ("GIFT_ID_INVALID",        "That gift doesn't exist — check the Gift ID."),
        ],
    },
}

GIFTS_DATA = [
    {"ru": "Новогодняя елка",       "en": "Christmas Tree",       "emoji": "🎄", "stars": 50,  "id": 5922558454332916696},
    {"ru": "Новогодний мишка",      "en": "New Year Bear",        "emoji": "🐻", "stars": 50,  "id": 5956217000635139069},
    {"ru": "Сердце 14 февраля",     "en": "Valentine Heart",      "emoji": "❤️", "stars": 50,  "id": 5801108895304779062},
    {"ru": "Мишка 14 февраля",      "en": "Valentine Bear",       "emoji": "🐻", "stars": 50,  "id": 5800655655995968830},
    {"ru": "Мишка 8 марта",         "en": "Women's Day Bear",     "emoji": "🐻", "stars": 50,  "id": 5866352046986232958},
    {"ru": "Мишка 17 марта",        "en": "March 17th Bear",      "emoji": "🐻", "stars": 50,  "id": 5893356958802511476},
    {"ru": "Первоапрельский мишка", "en": "April Fools Bear",     "emoji": "🐻", "stars": 50,  "id": 5893356958802511476},
    {"ru": "Пасхальный мишка",      "en": "Easter Bear",          "emoji": "🐻", "stars": 50,  "id": 5969796561943660080},
    {"ru": "Первомайский мишка",    "en": "May Day Bear",         "emoji": "🐻", "stars": 50,  "id": 6026193266406327981},
    {"ru": "Футбольный мишка",      "en": "Soccer Bear",          "emoji": "⚽", "stars": 50,  "id": 5974210632977745012},
    {"ru": "Кастомный ID",          "en": "Custom ID",            "emoji": "✏️", "stars": None, "id": None},
]


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
        print(f"⚠️  {e}")


def friendly_error(e: Exception, S: dict) -> str:
    raw = str(e) or type(e).__name__
    name = type(e).__name__

    simple = S["errors"].get(name)
    if simple is None:
        for key, text in S["error_substrings"]:
            if key in raw:
                simple = text
                break
    if simple is None:
        simple = S["err_unknown"]

    return f"❌ {simple}\n   ({name}: {raw})"


def input_with_counter(prompt: str, max_len: int) -> str:
    text = []

    def redraw():
        remaining = max_len - len(text)
        line = f"\r{prompt}{''.join(text)}  [{remaining}/{max_len}]"
        sys.stdout.write(line + "          \r" + line)
        sys.stdout.flush()

    redraw()
    while True:
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
            msvcrt.getwch()
        else:
            chars = [ch]
            while msvcrt.kbhit():
                nx = msvcrt.getwch()
                if nx in ("\r", "\n", "\x03", "\x00", "\xe0"):
                    if nx in ("\r", "\n"):
                        for c in chars:
                            if len(text) < max_len:
                                text.append(c)
                        print()
                        return "".join(text)
                    break
                chars.append(nx)
            for c in chars:
                if len(text) < max_len:
                    text.append(c)
            redraw()
            if len(text) >= max_len:
                sys.stdout.write(f"  [0/{max_len}] ⚠️")
                sys.stdout.flush()

    return "".join(text)


def print_qr_console(url: str):
    import qrcode
    qr = qrcode.QRCode(border=1)
    qr.add_data(url)
    qr.make(fit=True)
    matrix = qr.get_matrix()
    print()
    for row in matrix:
        line = "".join("██" if cell else "  " for cell in row)
        print(f"  {line}")
    print()


async def authorize_qr(app, S: dict):
    import base64
    from pyrogram.raw import functions as raw_fn, types as raw_t
    from pyrogram.errors import SessionPasswordNeeded

    print(S["qr_opening"])
    print(S["qr_hint"])

    r = await app.invoke(raw_fn.auth.ExportLoginToken(
        api_id=app.api_id,
        api_hash=app.api_hash,
        except_ids=[],
    ))
    token_b64 = base64.urlsafe_b64encode(r.token).decode().rstrip("=")
    url       = f"tg://login?token={token_b64}"
    print_qr_console(url)
    print(S["qr_waiting"])

    deadline = asyncio.get_event_loop().time() + 180
    while asyncio.get_event_loop().time() < deadline:
        await asyncio.sleep(20)
        try:
            r2 = await app.invoke(raw_fn.auth.ExportLoginToken(
                api_id=app.api_id,
                api_hash=app.api_hash,
                except_ids=[],
            ))
            if not isinstance(r2, raw_t.auth.LoginToken):
                return True
            if r2.token != r.token:
                token_b64 = base64.urlsafe_b64encode(r2.token).decode().rstrip("=")
                url = f"tg://login?token={token_b64}"
                print_qr_console(url)
                print(S["qr_waiting"])
                r = r2
        except SessionPasswordNeeded:
            print(S["qr_2fa"])
            from pyrogram.utils import compute_password_check
            pwd_info = await app.invoke(raw_fn.account.GetPassword())
            pwd = input(S["qr_2fa_p"]).strip()
            await app.invoke(raw_fn.auth.CheckPassword(
                password=compute_password_check(pwd_info, pwd)
            ))
            return True
        except Exception as e:
            err = str(e)
            if "SESSION_PASSWORD_NEEDED" in err:
                print(S["qr_2fa"])
                pwd = input(S["qr_2fa_p"]).strip()
                await app.check_password(pwd)
                return True
            print(friendly_error(e, S))
            return True

    print(S["qr_expired"])
    return False


def print_gift_menu(S: dict, lang: str):
    print()
    print("=" * 60)
    print(S["gifts_title"])
    print("-" * 60)
    for i, g in enumerate(GIFTS_DATA, 1):
        stars = f"⭐ {g['stars']}" if g["stars"] else "   ?"
        name  = g[lang]
        print(f"   {i:>2}) {g['emoji']} {name:<26} {stars}")
    print("-" * 60)


def choose_gift(S: dict, lang: str):
    print_gift_menu(S, lang)
    n = len(GIFTS_DATA)
    while True:
        s = input(S["gifts_prompt"].format(n=n)).strip()
        if not s or is_back(s):
            return None

        if s.isdigit() and 1 <= int(s) <= n:
            gift = GIFTS_DATA[int(s) - 1]
            if gift["id"] is None:
                while True:
                    cid = input(S["gifts_custom_id"]).strip()
                    if not cid or is_back(cid):
                        print_gift_menu(S, lang)
                        break
                    if cid.isdigit():
                        print(S["gifts_selected"].format(emoji=gift["emoji"], name=f"ID {cid}"))
                        return int(cid), f"{gift['emoji']} ID {cid}"
                    print(S["gifts_invalid_id"])
                continue
            else:
                print(S["gifts_selected"].format(emoji=gift["emoji"], name=gift[lang]))
                return gift["id"], f"{gift['emoji']} {gift[lang]}"
        print(S["gifts_invalid"].format(n=n))


def get_credentials(S: dict) -> tuple[int, str, str]:
    config = load_config()

    if config.get("api_id") and config.get("api_hash"):
        return config["api_id"], config["api_hash"], config.get("session_name", "gift_session")

    print()
    print("=" * 60)
    print(S["api_title"])
    print("-" * 60)
    print(S["api_hint"])
    print("-" * 60)

    while True:
        s = input(S["api_id_prompt"]).strip()
        if s.isdigit():
            api_id = int(s)
            break
        print(S["api_id_err"])

    while True:
        api_hash = input(S["api_hash_prompt"]).strip()
        if len(api_hash) >= 10:
            break
        print(S["api_hash_err"])

    print()
    session_name = input(S["session_prompt"]).strip() or "gift_session"
    print(S["session_ok"].format(name=session_name))

    save_config({"api_id": api_id, "api_hash": api_hash, "session_name": session_name})
    print(S["config_saved"])

    return api_id, api_hash, session_name


def format_user_name(user) -> str:
    uname = user.first_name or ""
    if user.last_name:
        uname += f" {user.last_name}"
    if user.username:
        uname += f" (@{user.username})"
    return uname


async def login(api_id: int, api_hash: str, session_name: str, S: dict):
    from pyrogram import Client
    from pyrogram.errors import AuthKeyUnregistered

    workdir      = APPDATA_DIR
    session_path = os.path.join(workdir, session_name + ".session")

    print()
    print("=" * 60)
    print(S["login_title"])
    print("=" * 60)

    max_attempts = 3
    for attempt in range(1, max_attempts + 1):
        already_auth = os.path.exists(session_path)
        login_method = "phone"
        if not already_auth:
            print()
            print(S["login_method"])
            print("-" * 60)
            while True:
                m = input(S["login_method_p"]).strip()
                if m in ("1", "2"):
                    login_method = "phone" if m == "1" else "qr"
                    break
                print(S["login_method_err"])

        import builtins
        _orig_input = builtins.input

        def _patched_input(prompt=""):
            if "phone number" in prompt.lower() or "bot token" in prompt.lower():
                if login_method == "qr":
                    return "qrcode"
                print()
                print(S["phone_hint"])
                print("-" * 60)
                return _orig_input(S["phone_prompt"]).strip()
            if "code" in prompt.lower():
                return _orig_input(S["code_prompt"]).strip()
            if "password" in prompt.lower():
                return _orig_input(S["password_prompt"]).strip()
            return _orig_input(prompt)

        builtins.input = _patched_input
        app = Client(name=session_name, api_id=api_id, api_hash=api_hash, workdir=workdir)

        try:
            if login_method == "qr" and not already_auth:
                builtins.input = _orig_input
                await app.connect()
                ok = await authorize_qr(app, S)
                if not ok:
                    try:
                        await app.disconnect()
                    except Exception:
                        pass
                    if attempt < max_attempts:
                        print(S["login_retry"])
                        continue
                    print(S["login_failed"])
                    return None
                await app.storage.save()
                print(S["qr_ok"])
                me = await app.get_me()
            else:
                await app.start()
                builtins.input = _orig_input
                me = await app.get_me()

        except AuthKeyUnregistered as e:
            builtins.input = _orig_input
            print(friendly_error(e, S))
            try:
                await app.disconnect()
            except Exception:
                pass
            for ext in ("", "-journal", "-wal", "-shm"):
                p = session_path + ext
                if os.path.exists(p):
                    try:
                        os.remove(p)
                    except OSError:
                        pass
            print(S["session_reset"])
            if attempt < max_attempts:
                print(S["login_retry"])
                continue
            print(S["login_failed"])
            return None

        except Exception as e:
            builtins.input = _orig_input
            print(friendly_error(e, S))
            try:
                await app.disconnect()
            except Exception:
                pass
            if attempt < max_attempts:
                print(S["login_retry"])
                continue
            print(S["login_failed"])
            return None

        finally:
            builtins.input = _orig_input

        display_name = format_user_name(me)
        print(f"\n{S['logged_as']}{display_name}")
        return app

    print(S["login_failed"])
    return None


async def run_order(app, S: dict, lang: str):
    STEP_GIFT, STEP_RECIPIENT, STEP_MESSAGE, STEP_ANON, STEP_CONFIRM, STEP_SEND = range(6)

    gift_id = gift_label = None
    recipient_user = recipient_display = None
    message_text = ""
    hide_name = False

    step = STEP_GIFT
    while True:
        if step == STEP_GIFT:
            picked = choose_gift(S, lang)
            if picked is None:
                print(S["order_cancelled"])
                return
            gift_id, gift_label = picked
            step = STEP_RECIPIENT

        elif step == STEP_RECIPIENT:
            print()
            print("=" * 60)
            print(S["recipient_title"])
            print("-" * 60)
            print(S["recipient_hint"])
            print(S["recipient_back"])
            print("-" * 60)
            raw = input(S["recipient_prompt"]).strip().lstrip("@")
            if not raw or is_back(raw):
                step = STEP_GIFT
                continue

            print(S["recipient_search"].format(r=raw))
            try:
                user = await app.get_users(raw)
            except Exception as e:
                print(friendly_error(e, S))
                print(S["recipient_tip"])
                continue

            recipient_user = user
            recipient_display = format_user_name(user)
            print(f"{S['recipient_found']}{recipient_display}")
            step = STEP_MESSAGE

        elif step == STEP_MESSAGE:
            print()
            print("=" * 60)
            print(S["msg_title"])
            print("-" * 60)
            msg = input_with_counter(S["msg_prompt"], MAX_MSG_LEN)
            if is_back(msg):
                step = STEP_RECIPIENT
                continue
            message_text = msg
            step = STEP_ANON

        elif step == STEP_ANON:
            print()
            print("=" * 60)
            print(S["anon_title"])
            print("-" * 60)
            print(S["anon_hint"])
            print("-" * 60)
            raw = input(S["anon_prompt"]).strip().lower()
            if is_back(raw):
                step = STEP_MESSAGE
                continue
            hide_name = raw in S["yes_values"]
            step = STEP_CONFIRM

        elif step == STEP_CONFIRM:
            print()
            print("=" * 60)
            print(S["confirm_title"])
            print("-" * 60)
            print(f"{S['confirm_gift']}{gift_label}")
            print(f"{S['confirm_rcpt']}{recipient_display}")
            print(f"{S['confirm_msg']}{message_text or S['confirm_no_msg']}")
            print(f"{S['confirm_anon']}{S['confirm_yes'] if hide_name else S['confirm_no']}")
            print("-" * 60)

            raw = input(S["confirm_prompt"]).strip().lower()
            if is_back(raw):
                step = STEP_ANON
                continue
            if raw in S["yes_values"]:
                step = STEP_SEND
            else:
                print(S["confirm_cancel"])
                return

        elif step == STEP_SEND:
            await send_gift_order(app, S, gift_id, recipient_user, message_text, hide_name)
            return


async def send_gift_order(app, S: dict, gift_id: int, user, message_text: str, hide_name: bool):
    from pyrogram.raw import functions, types as raw_types

    print(S["sending"])
    try:
        peer = await app.resolve_peer(user.id)
        message_obj = (
            raw_types.TextWithEntities(text=message_text, entities=[])
            if message_text else None
        )

        invoice = raw_types.InputInvoiceStarGift(
            peer=peer,
            gift_id=gift_id,
            hide_name=hide_name,
            message=message_obj,
        )

        payment_form = await app.invoke(functions.payments.GetPaymentForm(invoice=invoice))

        if hasattr(payment_form, "invoice") and payment_form.invoice.prices:
            stars = payment_form.invoice.prices[0].amount
            print(S["cost"].format(stars=stars))

        await app.invoke(functions.payments.SendStarsForm(
            form_id=payment_form.form_id,
            invoice=invoice,
        ))

        print(S["success"])
        print(S["delivered"].format(name=user.first_name))

    except Exception as e:
        print(friendly_error(e, S))


async def main():
    if sys.platform.startswith("win"):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    print()
    print(STRINGS["ru"]["choose_lang"])
    while True:
        choice = input(STRINGS["ru"]["lang_prompt"]).strip()
        if choice == "1":
            S = STRINGS["ru"]
            lang = "ru"
            break
        elif choice == "2":
            S = STRINGS["en"]
            lang = "en"
            break

    print(f"\n{S['welcome']}\n")

    api_id, api_hash, session_name = get_credentials(S)

    app = await login(api_id, api_hash, session_name, S)
    if app is None:
        input()
        return

    try:
        while True:
            await run_order(app, S, lang)
            print()
            if input(S["again_prompt"]).strip().lower() not in S["yes_values"]:
                print(S["goodbye"])
                break
            print()
    finally:
        try:
            await app.stop()
        except Exception:
            try:
                await app.disconnect()
            except Exception:
                pass
        print(S["disconnected"])
        print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
