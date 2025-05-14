from smartcard.System import readers
import requests
import time

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
            response = requests.post("http://192.168.157.15:5000/admin/nfc-update", json={"nfc_id": nfc_id})
            print("📨 Sent to Flask:", response.text)   
            break

    except Exception as e:
        print("⛔ No card or connection failed:", e)
        time.sleep(1)
    