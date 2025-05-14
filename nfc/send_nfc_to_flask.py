from smartcard.System import readers
import requests
import time

RAILWAY_URL = "https://nfc-asset-tracking-production.up.railway.app"

r = readers()
if not r:
    print("❌ No NFC reader found. Make sure the driver is installed.")
    exit()

reader = r[0].createConnection()
last_uid = None

while True:
    try:
        reader.connect()
        print("📡 Waiting for NFC tag...")
        command = [0xFF, 0xCA, 0x00, 0x00, 0x00]
        response, sw1, sw2 = reader.transmit(command)

        if sw1 == 0x90:
            nfc_id = ''.join('{:02X}'.format(x) for x in response)

            # Only process if it's a new scan (not the same tag)
            if nfc_id != last_uid:
                print("✅ UID:", nfc_id)

                # Send to Railway
                response = requests.post(f"{RAILWAY_URL}/admin/nfc-update", json={"nfc_id": nfc_id})
                print("📨 Sent to Railway Flask:", response.text)

                # Optionally send to register/out/in
                requests.post(f"{RAILWAY_URL}/admin/admin-register-item", json={"nfc_id": nfc_id})
                requests.post(f"{RAILWAY_URL}/admin/out", json={"nfc_id": nfc_id})
                requests.post(f"{RAILWAY_URL}/admin/in", json={"nfc_id": nfc_id})

                last_uid = nfc_id
                print("🕒 Waiting for tag removal...")

            else:
                print("⚠️ Same tag detected, waiting for new tag...")

        time.sleep(0.5)

    except Exception as e:
        # When no tag is present
        last_uid = None
        print("⛔ No card or connection failed:", e)
        time.sleep(1)
