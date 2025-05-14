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
last_sent_time = 0

while True:
    try:
        reader.connect()
        print("📡 Waiting for NFC tag...")
        command = [0xFF, 0xCA, 0x00, 0x00, 0x00]
        response, sw1, sw2 = reader.transmit(command)

        if sw1 == 0x90:
            nfc_id = ''.join('{:02X}'.format(x) for x in response)

            # Only send if different or enough time has passed
            if nfc_id != last_uid or (time.time() - last_sent_time > 5):
                last_uid = nfc_id
                last_sent_time = time.time()

                print("✅ UID:", nfc_id)

                requests.post(f"{RAILWAY_URL}/admin/nfc-update", json={"nfc_id": nfc_id})
                print("📨 Sent to Railway")

                requests.post(f"{RAILWAY_URL}/admin/admin-register-item", json={"nfc_id": nfc_id})
                requests.post(f"{RAILWAY_URL}/admin/out", json={"nfc_id": nfc_id})
                requests.post(f"{RAILWAY_URL}/admin/in", json={"nfc_id": nfc_id})

        time.sleep(1)

    except Exception as e:
        # Reset if error or no tag
        print("⛔ No card or connection failed:", e)

        if last_uid is not None:
            print("🧹 Clearing last UID due to removal or error.")
            last_uid = None
            try:
                requests.post(f"{RAILWAY_URL}/admin/nfc-update", json={"nfc_id": ""})
                print("📨 Cleared UID in Railway")
            except:
                print("⚠️ Failed to notify Railway about UID clear.")

        time.sleep(1)
