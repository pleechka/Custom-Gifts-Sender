# 🎁 Custom Gifts Sender

---

### What is this?

**Custom Gifts Sender** is a Windows console app that lets you send Telegram Star Gifts to any user directly from your PC. No bots, no third-party services — it works through the official Telegram API using your own account.

### Features

- 🎄 Built-in gift menu with popular gifts (New Year Tree, Teddy Bear, Valentine's Heart and more)
- ✏️ Custom Gift ID support — send any gift by its ID
- 📱 Two login methods: **phone number** or **QR code**
- 🕵️ Anonymous mode 
- 💌 Message support
- 💾 Settings are saved to `config.json` — no need to re-enter API credentials on next launch



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

## ⚠️ Disclaimer

This tool uses the official Telegram API for personal use only. Use responsibly and in accordance with [Telegram's Terms of Service](https://telegram.org/tos). The author is not responsible for any misuse.
