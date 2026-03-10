# 🎁 Custom Gifts Sender

> Send Telegram Star Gifts to any user — with a gift menu, QR login, anonymous mode and message support.

---

## 🇬🇧 English

### What is this?

**Custom Gifts Sender** is a Windows console app that lets you send Telegram Star Gifts to any user directly from your PC. No bots, no third-party services — it works through the official Telegram API using your own account.

### Features

- 🎄 Built-in gift menu with popular gifts (New Year Tree, Teddy Bear, Valentine's Heart and more)
- ✏️ Custom Gift ID support — send any gift by its ID
- 📱 Two login methods: **phone number** or **QR code** (opens a popup window)
- 🕵️ Anonymous mode — hide your name from the recipient
- 💌 Message support with a live **128-character counter**
- 💾 Settings are saved to `config.json` — no need to re-enter API credentials on next launch
- 📦 Can be compiled to a standalone `.exe` — no Python required on the target machine

### Requirements

- Windows 10/11
- Python 3.10+ (only needed to run from source)
- Telegram account
- API credentials from [my.telegram.org](https://my.telegram.org)

### Installation & Run

```bash
# 1. Clone the repo
git clone https://github.com/YOUR_USERNAME/Custom-Gifts-Sender.git
cd Custom-Gifts-Sender

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run
python gift_sender.py
```

### Build EXE

```bash
pyinstaller --onefile --console ^
  --hidden-import pyrogram ^
  --hidden-import qrcode ^
  --hidden-import PIL ^
  --hidden-import tkinter ^
  --collect-all pyrogram ^
  --collect-all qrcode ^
  gift_sender.py
```

The ready `.exe` will be in the `dist/` folder. Place `config.json` and the `.session` file next to it on subsequent runs.

### How to get API credentials

1. Go to [my.telegram.org](https://my.telegram.org)
2. Log in with your phone number
3. Click **API development tools**
4. Create an app (any name)
5. Copy `App api_id` and `App api_hash`

### Notes

- `config.json` — stores your API credentials (keep it private, don't share)
- `*.session` — your Telegram session file (keep it private, don't share)
- Both files are created automatically on first run next to the script / `.exe`

---

## 🇷🇺 Русский

### Что это?

**Custom Gifts Sender** — консольное приложение для Windows, которое позволяет отправлять Telegram Star Gifts любому пользователю прямо с компьютера. Без ботов и сторонних сервисов — работает через официальный Telegram API с вашего аккаунта.

### Возможности

- 🎄 Встроенное меню подарков с популярными подарками (Новогодняя елка, Мишка, Сердце и другие)
- ✏️ Поддержка кастомного Gift ID — отправьте любой подарок по его ID
- 📱 Два способа входа: **по номеру телефона** или **по QR-коду** (открывается отдельное окно)
- 🕵️ Анонимный режим — скройте своё имя от получателя
- 💌 Поддержка сообщения с живым счётчиком на **128 символов**
- 💾 Настройки сохраняются в `config.json` — не нужно вводить API-данные при каждом запуске
- 📦 Компилируется в `.exe` — не требует Python на целевой машине

### Требования

- Windows 10/11
- Python 3.10+ (только для запуска из исходников)
- Аккаунт Telegram
- API-ключи с [my.telegram.org](https://my.telegram.org)

### Установка и запуск

```bash
# 1. Клонировать репозиторий
git clone https://github.com/YOUR_USERNAME/Custom-Gifts-Sender.git
cd Custom-Gifts-Sender

# 2. Установить зависимости
pip install -r requirements.txt

# 3. Запустить
python gift_sender.py
```

### Сборка EXE

```bash
pyinstaller --onefile --console ^
  --hidden-import pyrogram ^
  --hidden-import qrcode ^
  --hidden-import PIL ^
  --hidden-import tkinter ^
  --collect-all pyrogram ^
  --collect-all qrcode ^
  gift_sender.py
```

Готовый `.exe` будет в папке `dist/`. При следующих запусках положите рядом `config.json` и файл `.session`.

### Как получить API-ключи

1. Зайдите на [my.telegram.org](https://my.telegram.org)
2. Войдите через свой номер телефона
3. Нажмите **API development tools**
4. Создайте приложение (название любое)
5. Скопируйте `App api_id` и `App api_hash`

### Важные файлы

- `config.json` — хранит ваши API-ключи (не передавайте посторонним)
- `*.session` — файл сессии Telegram (не передавайте посторонним)
- Оба файла создаются автоматически при первом запуске рядом со скриптом / `.exe`

---

## ⚠️ Disclaimer

This tool uses the official Telegram API for personal use only. Use responsibly and in accordance with [Telegram's Terms of Service](https://telegram.org/tos). The author is not responsible for any misuse.
