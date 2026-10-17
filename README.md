# راصد (RAASED)

وكيل ذكي لمراقبة أحواض الاستزراع السمكي المغلقة واكتشاف أعطال الحساسات، يحلل القراءات عبر Gemini ويرسل التنبيهات إلى تيليجرام.

## المكونات

- `main.py`: خادم Flask يستقبل القراءات على `POST /reading` ويخزنها في SQLite (`rased.db`)، ويحلل آخر القراءات كل دقيقتين ويرسل النتيجة إلى تيليجرام.
- `demo_sensor.py`: محاكاة حساسات ترسل قراءات تجريبية إلى الخادم كل دقيقة.

## التشغيل

```bash
pip install -r requirements.txt
```

ضع قيمًا حقيقية لـ `GEMINI_API_KEY` و`TELEGRAM_BOT_TOKEN` و`TELEGRAM_CHAT_ID` في `main.py`، ثم:

```bash
python main.py
python demo_sensor.py   # في نافذة أخرى
```
