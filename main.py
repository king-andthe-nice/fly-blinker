import json
import time
import os
import paho.mqtt.client as mqtt
import ssl
from serverchan_sdk import sc_send

# ===================== 你的配置 =====================
MY_CLIENT_ID = "3"
MY_USER_ID   = "3"
MY_PASSWORD  = "3"
TARGET_DEVICE = "9B9A77D5PLBP22KLCRYNH4S5"
SERVERCHAN_SENDKEY = "SCT346756TC2fPdtaZVPV1P8rrGep9icgK"
WAIT_TIMEOUT = 4
CHECK_INTERVAL = 10  # 每10秒检查一次
# ====================================================

STATE_FILE = "last_state.txt"

def on_connect(client, userdata, flags, rc, reasonCode):
    client.subscribe(f"/device/{MY_CLIENT_ID}/r")
    payload = {
        "fromDevice": MY_CLIENT_ID,
        "toDevice": TARGET_DEVICE,
        "deviceType": "DiyArduino",
        "data": {"get": "state"}
    }
    client.publish(f"/device/{MY_CLIENT_ID}/s", json.dumps(payload))

def on_message(client, userdata, msg):
    global result, got_response
    try:
        data = json.loads(msg.payload.decode())
        if "data" in data and "state" in data["data"]:
            result = "online"
            got_response = True
    except:
        pass

def send_wechat(title, content):
    try:
        sc_send(SERVERCHAN_SENDKEY, title, content)
        print("📩 微信通知已发送")
    except Exception as e:
        print("❌ 通知发送失败")

def get_last_state():
    if not os.path.exists(STATE_FILE):
        return None
    with open(STATE_FILE, "r", encoding="utf-8") as f:
        return f.read().strip()

def save_state(state):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        f.write(state)

def check_device():
    global result, got_response
    result = None
    got_response = False

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, MY_CLIENT_ID, protocol=mqtt.MQTTv311)
    client.username_pw_set(MY_USER_ID, MY_PASSWORD)
    client.tls_set(cert_reqs=ssl.CERT_NONE)
    client.tls_insecure_set(True)
    client.on_connect = on_connect
    client.on_message = on_message

    try:
        client.connect("broker.diandeng.tech", 1884, 60)
    except:
        return "offline"

    client.loop_start()
    start = time.time()
    while time.time() - start < WAIT_TIMEOUT:
        if got_response:
            break
        time.sleep(0.2)
    client.loop_stop()
    client.disconnect()
    return result if result == "online" else "offline"

if __name__ == "__main__":
    print("="*50)
    print("      Blinker 设备 24 小时在线监控工具")
    print("="*50)

    while True:
        current_state = check_device()
        last_state = get_last_state()

        print(f"\r[{time.ctime()}] 设备状态: {current_state}", end="")

        if last_state != current_state:
            print("\n🔔 状态变化！")
            if current_state == "online":
                send_wechat("设备已上线", "✅ 设备恢复在线")
            else:
                send_wechat("设备已离线", "❌ 设备断开连接")
            save_state(current_state)

        time.sleep(CHECK_INTERVAL)
