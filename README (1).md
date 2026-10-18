# Personal AI Agent — Render Simple Deploy (MVP)

এই সংস্করণটি আগের Link Shortener Bot-এর মতো একটি GitHub repository থেকে Render-এর একটি Docker Web Service হিসেবে deploy করার জন্য সাজানো। Render Environment-এ মাত্র এই তিনটি variable দিতে হবে: `OWNER_TELEGRAM_ID`, `BOT_TOKEN`, `AI_API_KEY`। `AI_API_KEY`-এর মধ্যে Primary ও Backup Grok key দিতে চাইলে `primary_key,backup_key` ফরম্যাটে কমা দিয়ে আলাদা করো। Render-এ একই নামের variable দুবার তৈরি করবে না।

## Deploy
1. ZIP extract করো। `personal-ai-agent` ফোল্ডারের ভেতরের ফাইলগুলো GitHub repository root-এ upload করো; ZIP-কে ZIP হিসেবেই upload কোরো না।
2. Render Dashboard → New + → Web Service অথবা Blueprint-এ repository connect করো। Blueprint ব্যবহার করলে `render.yaml` থেকে service তৈরি হবে।
3. Environment-এ `OWNER_TELEGRAM_ID`, `BOT_TOKEN`, `AI_API_KEY` সেট করো।
4. Deploy শেষে `https://YOUR-SERVICE.onrender.com/health` খুলে health response দেখো, তারপর Telegram bot-এ `/start` পাঠাও।

## Important limitations
- এই MVP একটি web service-এ Telegram polling process ও FastAPI চালায়, আলাদা worker/DB প্রয়োজন হয় না। Render free service-এ sleep/restart হতে পারে; bot সবসময় অনলাইনে থাকবে এমন নিশ্চয়তা নেই।
- SQLite ডেটা Render-এর ephemeral filesystem-এ থাকে; redeploy/restart-এর পর নোট/টাস্ক হারাতে পারে। স্থায়ী ডেটার জন্য PostgreSQL লাগবে, যা অতিরিক্ত `DATABASE_URL` চাইবে।
- `AI_API_KEY`-এ দুটি key দিলে code প্রথম key ব্যর্থ হলে দ্বিতীয়টি চেষ্টা করবে। API provider/model error হলে backup-ও ব্যর্থ হতে পারে।
- Android app এখনও UI scaffold; APK তৈরি হয়নি এবং ফোন নিয়ন্ত্রণের বাস্তব action এখনও নেই।
- API-তে production-grade authentication/device pairing এখনও সম্পূর্ণ নয়। Public internet-এ sensitive কাজের জন্য ব্যবহার কোরো না।
- কোনো API key GitHub-এ commit করবে না বা চ্যাটে পাঠাবে না।
