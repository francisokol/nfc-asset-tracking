from smartcard.System import readers
import requests
import time

# ✅ Replace this with your actual Railway app URL
RAILWAY_URL = "https://your-railway-app.up.railway.app"

r = readers()
if not r:
    print("❌ No NFC reader found. Make sure the driver is installed.")
    exit()

reader = r[0].createConnection()

while True:
    try:
        reader.connect()
        print("📡 Waiting for NFC tag...")
        command = [0xFF, 0xCA, 0x00, 0x00, 0x00]
        response, sw1, sw2 = reader.transmit(command)

        if sw1 == 0x90:
            nfc_id = ''.join('{:02X}'.format(x) for x in response)
            print("✅ UID:", nfc_id)

            # 🔁 Send NFC data to the Railway-hosted Flask app
            try:
                response = requests.post(f"{RAILWAY_URL}/admin/nfc-update", json={"nfc_id": nfc_id})
                print("📨 Sent to Railway Flask:", response.text)
            except requests.exceptions.RequestException as e:
                print("❌ Failed to send to Railway Flask:", e)

            break

    except Exception as e:
        print("⛔ No card or connection failed:", e)
        time.sleep(1)
