from fastapi.testclient import TestClient
from backend.main import app
from backend.config import settings

def test_health():
    r=TestClient(app).get('/health')
    assert r.status_code == 200
    assert r.json()['status'] == 'ok'

def test_owner_rejected_when_unconfigured():
    old=settings.owner_telegram_id
    settings.owner_telegram_id=0
    try:
        r=TestClient(app).post('/api/tasks',json={'owner_id':'123','title':'test','details':''})
        assert r.status_code == 403
    finally: settings.owner_telegram_id=old
