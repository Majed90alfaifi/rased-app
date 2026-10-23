# RAASED

**An AI agent for detecting sensor faults in closed aquaculture systems.**

RAASED (Arabic: راصد, "the observer") collects water-quality readings from fish ponds, analyzes them with Google Gemini to spot faulty sensors and abnormal conditions, and sends a concise alert with recommendations to the operator on Telegram.

---

## Features

- **Reading ingestion:** a lightweight REST endpoint accepts sensor readings.
- **Persistent storage:** every reading is stored in a local SQLite database.
- **Fault detection:** trend analysis flags stuck sensors, implausible jumps, and outliers.
- **Correlation analysis:** related indicators are evaluated together, for example rising ammonia alongside falling dissolved oxygen.
- **Risk assessment:** each analysis is rated *Low*, *Medium*, *High*, or *Critical*, with a short-term forecast.
- **Automated alerts:** findings and recommended actions are sent to Telegram every two minutes.

## Monitored Parameters

| Parameter         | Field              |
|-------------------|--------------------|
| Temperature       | `temperature`      |
| pH                | `ph`               |
| Ammonia           | `ammonia`          |
| Water level       | `water_level`      |
| Dissolved oxygen  | `dissolved_oxygen` |

## Architecture

```
Sensors ──► RAASED server (Flask) ──► SQLite database
                                            │
                Telegram ◄── Gemini analysis ┘
```

1. Sensors (or the included simulator) `POST` readings to the Flask server.
2. Readings are written to `rased.db`.
3. A background worker runs every 120 seconds. It loads the latest readings for the pond and asks Gemini for a structured assessment.
4. The assessment is delivered to the configured Telegram chat.

## Getting Started

### Prerequisites

- Python 3.9 or later
- A [Google Gemini API key](https://aistudio.google.com/apikey)
- A Telegram bot token (from [@BotFather](https://t.me/BotFather)) and the target chat ID

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure credentials

Set the following constants at the top of `main.py`:

| Variable             | Description                              |
|----------------------|------------------------------------------|
| `GEMINI_API_KEY`     | Google Gemini API key                    |
| `TELEGRAM_BOT_TOKEN` | Telegram bot token                       |
| `TELEGRAM_CHAT_ID`   | Chat ID that receives the alerts         |

> **Security note:** never commit real credentials to version control.

### 3. Run the server

```bash
python main.py
```

The server listens on port `5000`. It creates the database automatically on first run.

### 4. Run the sensor simulator (optional)

In a separate terminal, start the simulator. It sends one reading per minute, in a scenario where the pond's water quality gets steadily worse:

```bash
python demo_sensor.py
```

## API Reference

### `POST /reading`

Submits a new sensor reading.

**Request body**

```json
{
  "pond_id": 1,
  "temperature": 28,
  "ph": 7.5,
  "ammonia": 1.0,
  "water_level": 90,
  "dissolved_oxygen": 7.0
}
```

All fields are required.

**Response**

```json
{
  "status": "saved",
  "data": { "...": "the submitted reading" }
}
```

## Sample Alert

Alerts are generated in Arabic. A typical message:

<div dir="rtl">

```
🤖 راصد - الحوض 1

📊 الاتجاه العام:
ارتفاع مستمر في الأمونيا مع انخفاض الأكسجين.

⚠️ مستوى الخطر:
مرتفع

🔧 حالة الحساسات:
قفزة مفاجئة في درجة الحرارة قد تشير إلى عطل في الحساس.

✅ التوصية:
فحص حساس الحرارة وتشغيل التهوية فورًا.
```

</div>

**English translation**

```
🤖 RAASED - Pond 1

📊 Overall trend:
Steady rise in ammonia with declining dissolved oxygen.

⚠️ Risk level:
High

🔧 Sensor status:
A sudden jump in temperature may indicate a faulty sensor.

✅ Recommendation:
Inspect the temperature sensor and start aeration immediately.
```

## Project Structure

```
rased_app/
├── main.py            # API server, analysis worker, and Telegram alerts
├── demo_sensor.py     # Sensor simulator for testing
└── requirements.txt   # Python dependencies
```

## Current Limitations

- The analysis worker monitors pond `1` only.
- An analysis runs once at least 3 readings are stored, and it covers the 8 most recent readings.
- Credentials are hard-coded in `main.py` rather than loaded from environment variables.
