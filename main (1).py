from fastapi import FastAPI, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from backend.config import settings
from backend.database import Base, engine, get_db
from backend.models import Task, Note, Approval
from backend.schemas import ChatIn, TaskIn, NoteIn, ApprovalDecision
from backend.security import owner_allowed, is_public_url
from backend.ai import answer
import json

Base.metadata.create_all(bind=engine)
app=FastAPI(title="Personal AI Agent", version="0.1.0", description="Owner-controlled personal assistant MVP")

def require_owner(owner_id: str):
    if not owner_allowed(owner_id): raise HTTPException(403,"Owner authentication failed. Set OWNER_TELEGRAM_ID and use that exact ID.")

@app.get("/health")
def health(): return {"status":"ok","service":"personal-ai-agent","version":"0.1.0"}

@app.post("/api/chat")
async def chat(body: ChatIn):
    require_owner(body.owner_id)
    return {"reply": await answer(body.message), "note":"This MVP does not execute arbitrary phone actions."}

@app.post("/api/tasks")
def create_task(body: TaskIn, db: Session=Depends(get_db)):
    require_owner(body.owner_id)
    item=Task(owner_id=body.owner_id,title=body.title,details=body.details,status="pending")
    db.add(item); db.commit(); db.refresh(item)
    return {"id":item.id,"title":item.title,"details":item.details,"status":item.status}

@app.get("/api/tasks")
def list_tasks(owner_id: str, db: Session=Depends(get_db)):
    require_owner(owner_id)
    rows=db.query(Task).filter(Task.owner_id==owner_id).order_by(Task.id.desc()).limit(100).all()
    return [{"id":x.id,"title":x.title,"details":x.details,"status":x.status} for x in rows]

@app.post("/api/notes")
def add_note(body: NoteIn, db: Session=Depends(get_db)):
    require_owner(body.owner_id)
    n=Note(owner_id=body.owner_id,content=body.content); db.add(n); db.commit(); db.refresh(n)
    return {"id":n.id,"content":n.content,"status":"saved"}

@app.get("/api/notes")
def list_notes(owner_id: str, db: Session=Depends(get_db)):
    require_owner(owner_id)
    return [{"id":n.id,"content":n.content} for n in db.query(Note).filter(Note.owner_id==owner_id).order_by(Note.id.desc()).limit(100).all()]

@app.post("/api/approvals")
def request_approval(body: dict, db: Session=Depends(get_db)):
    owner_id=str(body.get("owner_id","")); require_owner(owner_id)
    action=str(body.get("action","")); payload=body.get("payload",{})
    allowed={"publish_telegram_post","send_message","delete_file","external_action"}
    if action not in allowed: raise HTTPException(400,"Unsupported approval action")
    a=Approval(owner_id=owner_id,action=action,payload=json.dumps(payload,ensure_ascii=False),status="pending")
    db.add(a); db.commit(); db.refresh(a)
    return {"id":a.id,"action":a.action,"payload":payload,"status":"pending","message":"Approval is recorded only; no action is executed by this endpoint."}

@app.post("/api/approvals/{approval_id}/decision")
def decide(approval_id: int, body: ApprovalDecision, db: Session=Depends(get_db)):
    require_owner(body.owner_id)
    a=db.query(Approval).filter(Approval.id==approval_id,Approval.owner_id==body.owner_id).first()
    if not a: raise HTTPException(404,"Approval not found")
    if a.status!="pending": raise HTTPException(409,"Approval already decided")
    a.status="approved" if body.approve else "rejected"; db.commit()
    return {"id":a.id,"status":a.status,"message":"Decision saved. This MVP deliberately does not execute the approved action."}

@app.post("/api/check-url")
def check_url(body: dict):
    owner_id=str(body.get("owner_id","")); require_owner(owner_id)
    url=str(body.get("url",""))
    return {"url":url,"allowed_by_basic_check":is_public_url(url),"warning":"Do not fetch untrusted URLs without redirect/IP re-validation and network egress controls."}
