import sqlite3
import time
import threading
import requests
from flask import Flask, request, jsonify
from google import genai

GEMINI_API_KEY = "GEMINI_API_KEY"
TELEGRAM_BOT_TOKEN = "TELEGRAM_BOT_TOKEN"
TELEGRAM_CHAT_ID = "TELEGRAM_CHAT_ID"

MODEL_NAME = "gemini-3.5-flash"

READ_ANALYSIS_INTERVAL = 120  # كل دقيقتين يرسل تحليل/تنبيه

app = Flask(__name__)
client = genai.Client(api_key=GEMINI_API_KEY)


def init_db():
    conn = sqlite3.connect("rased.db")
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS readings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pond_id INTEGER,
            temperature REAL,
            ph REAL,
            ammonia REAL,
            water_level REAL,
            dissolved_oxygen REAL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()


@app.route("/reading", methods=["POST"])
def add_reading():
    data = request.json

    conn = sqlite3.connect("rased.db")
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO readings
        (pond_id, temperature, ph, ammonia, water_level, dissolved_oxygen)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        data["pond_id"],
        data["temperature"],
        data["ph"],
        data["ammonia"],
        data["water_level"],
        data["dissolved_oxygen"]
    ))

    conn.commit()
    conn.close()

    return jsonify({"status": "saved", "data": data})


def get_history(pond_id=1, limit=8):
    conn = sqlite3.connect("rased.db")
    cur = conn.cursor()

    cur.execute("""
        SELECT created_at, temperature, ph, ammonia, water_level, dissolved_oxygen
        FROM readings
        WHERE pond_id = ?
        ORDER BY id DESC
        LIMIT ?
    """, (pond_id, limit))

    rows = cur.fetchall()
    conn.close()

    history = []

    for row in reversed(rows):
        history.append({
            "time": row[0],
            "temperature": row[1],
            "ph": row[2],
            "ammonia": row[3],
            "water_level": row[4],
            "dissolved_oxygen": row[5]
        })

    return history


def send_telegram(message):
    response = requests.post(
        f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
        json={
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message
        }
    )

    print(response.status_code)
    print(response.text)


def analyze_with_rased():
    history_data = get_history(pond_id=1)

    if len(history_data) < 3:
        print("Not enough history yet...")
        return

    latest = history_data[-1]

    prompt = f"""
أنت راصد (RAASED)، وكيل هندسي ذكي متخصص في اكتشاف أعطال الحساسات في نظام الاستزراع السمكي المغلق.

مهمتك الأساسية:
اكتشاف أعطال الحساسات أو القراءات غير الطبيعية، ثم توضيح أثرها على الحوض وإرسال توصية عملية للمسؤول.

القراءات التاريخية للحوض:
{history_data}

آخر قراءة:
{latest}

حلل البيانات من خلال:
1. اتجاه القراءات عبر الزمن.
2. احتمال وجود عطل أو تعليق في أحد الحساسات.
3. القفزات غير المنطقية أو القيم الشاذة.
4. العلاقة بين المؤشرات مثل ارتفاع الأمونيا مع انخفاض الأكسجين.
5. مستوى الخطر الحالي.
6. ما قد يحدث خلال الساعات القادمة إذا استمر الوضع.

اكتب رسالة تيليجرام قصيرة ومنظمة بهذا الشكل:

🤖 راصد - الحوض 1

📊 الاتجاه العام:
...

⚠️ مستوى الخطر:
منخفض / متوسط / مرتفع / حرج

🔧 حالة الحساسات:
...

🔍 السبب المحتمل:
...

📈 التوقع القادم:
...

✅ التوصية:
...

قواعد:
- لا تذكر أنك نموذج ذكاء اصطناعي.
- لا تجزم بالعطل، استخدم: "احتمال" أو "قد".
- ركز على اكتشاف أعطال الحساسات لأنها هدف التحدي.
- لا تطل الرسالة.
"""

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt
    )

    message = response.text
    send_telegram(message)
    print("Raased analysis sent.")


def monitor_loop():
    while True:
        try:
            analyze_with_rased()
        except Exception as e:
            print("Error:", e)

        time.sleep(READ_ANALYSIS_INTERVAL)


if __name__ == "__main__":
    init_db()

    thread = threading.Thread(target=monitor_loop)
    thread.daemon = True
    thread.start()

    app.run(host="0.0.0.0", port=5000)