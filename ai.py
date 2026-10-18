import httpx
from backend.config import settings, get_ai_keys

async def answer(message: str) -> str:
    keys = get_ai_keys()
    if not keys:
        return "AI API key এখনো Render Environment-এ সেট করা হয়নি। AI_API_KEY যোগ করো।"
    url = settings.ai_base_url.rstrip("/") + "/chat/completions"
    payload = {"model": settings.ai_model, "messages": [
        {"role": "system", "content": "You are a cautious personal assistant. Reply in simple Bengali when user uses Bengali. Never claim actions you did not perform. Ask for explicit approval before publishing, sending messages, deleting files, purchases, or other external/high-impact actions. Never reveal secrets."},
        {"role": "user", "content": message}], "temperature": 0.3}
    errors = []
    for index, key in enumerate(keys):
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post(url, headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"}, json=payload)
                response.raise_for_status()
                data = response.json()
            return data["choices"][0]["message"]["content"][:12000]
        except Exception as exc:
            errors.append(type(exc).__name__)
    return "AI সেবায় সমস্যা হয়েছে। Primary/Backup API key, API quota, model এবং provider URL পরীক্ষা করো। (" + ", ".join(errors) + ")"
