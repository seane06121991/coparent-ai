import uuid
import json
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional
from dotenv import load_dotenv
load_dotenv()
from database import init_db, DB_PATH
from agents import run_negotiation_round, summarize_agreement
import aiosqlite

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield

app = FastAPI(title="CoParent AI", version="1.0.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", include_in_schema=False)
async def root():
    return FileResponse("static/index.html")

class CreateFamilyRequest(BaseModel):
    child_names: list[str]
    parent_a_name: str
    parent_b_name: str
    parent_a_preferences: Optional[dict] = {}
    parent_b_preferences: Optional[dict] = {}

class UpdatePreferencesRequest(BaseModel):
    preferences: dict

class StartNegotiationRequest(BaseModel):
    family_id: str
    topic: str
    initiated_by: str
    context: Optional[dict] = {}

@app.post("/families")
async def create_family(req: CreateFamilyRequest):
    family_id = str(uuid.uuid4())
    parent_a_id = str(uuid.uuid4())
    parent_b_id = str(uuid.uuid4())
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("INSERT INTO families (id, child_names) VALUES (?, ?)", (family_id, json.dumps(req.child_names)))
        await db.execute("INSERT INTO parents (id, family_id, name, role, preferences) VALUES (?, ?, ?, ?, ?)", (parent_a_id, family_id, req.parent_a_name, "parent_a", json.dumps(req.parent_a_preferences)))
        await db.execute("INSERT INTO parents (id, family_id, name, role, preferences) VALUES (?, ?, ?, ?, ?)", (parent_b_id, family_id, req.parent_b_name, "parent_b", json.dumps(req.parent_b_preferences)))
        await db.commit()
    return {"family_id": family_id, "parent_a_id": parent_a_id, "parent_b_id": parent_b_id}

@app.get("/families/{family_id}")
async def get_family(family_id: str):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM families WHERE id = ?", (family_id,)) as cur:
            family = await cur.fetchone()
        if not family:
            raise HTTPException(404, "Family not found")
        async with db.execute("SELECT * FROM parents WHERE family_id = ?", (family_id,)) as cur:
            parents = await cur.fetchall()
    return {"id": family["id"], "child_names": json.loads(family["child_names"]), "parents": [{"id": p["id"], "name": p["name"], "role": p["role"], "preferences": json.loads(p["preferences"])} for p in parents]}

@app.patch("/parents/{parent_id}/preferences")
async def update_preferences(parent_id: str, req: UpdatePreferencesRequest):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT * FROM parents WHERE id = ?", (parent_id,)) as cur:
            parent = await cur.fetchone()
        if not parent:
            raise HTTPException(404, "Parent not found")
        await db.execute("UPDATE parents SET preferences = ? WHERE id = ?", (json.dumps(req.preferences), parent_id))
        await db.commit()
    return {"message": "Preferences updated"}

@app.post("/negotiations")
async def start_negotiation(req: StartNegotiationRequest):
    negotiation_id = str(uuid.uuid4())
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM families WHERE id = ?", (req.family_id,)) as cur:
            family = await cur.fetchone()
        if not family:
            raise HTTPException(404, "Family not found")
        async with db.execute("SELECT * FROM parents WHERE family_id = ?", (req.family_id,)) as cur:
            parents = await cur.fetchall()
        parent_a = next(p for p in parents if p["role"] == "parent_a")
        parent_b = next(p for p in parents if p["role"] == "parent_b")
        await db.execute("INSERT INTO negotiations (id, family_id, topic, initiated_by, context) VALUES (?, ?, ?, ?, ?)", (negotiation_id, req.family_id, req.topic, req.initiated_by, json.dumps(req.context)))
        await db.commit()
    child_names = json.loads(family["child_names"])
    result = await run_negotiation_round(negotiation_id=negotiation_id, family_id=req.family_id, parent_a={"name": parent_a["name"], "preferences": json.loads(parent_a["preferences"])}, parent_b={"name": parent_b["name"], "preferences": json.loads(parent_b["preferences"])}, child_names=child_names, topic=req.topic, history=[])
    async with aiosqlite.connect(DB_PATH) as db:
        for msg in result["rounds"]:
            await db.execute("INSERT INTO messages (negotiation_id, sender, role, content) VALUES (?, ?, ?, ?)", (negotiation_id, msg["sender"], msg["role"], msg["content"]))
        final_agreement = None
        if result["status"] == "agreed" and result["agreement"]:
            final_agreement = summarize_agreement(req.topic, result["agreement"], child_names)
        await db.execute("UPDATE negotiations SET status = ?, final_agreement = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?", (result["status"], final_agreement, negotiation_id))
        await db.commit()
    return {"negotiation_id": negotiation_id, "topic": req.topic, "status": result["status"], "rounds": result["rounds"], "agreement": final_agreement}

@app.get("/negotiations/{negotiation_id}")
async def get_negotiation(negotiation_id: str):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM negotiations WHERE id = ?", (negotiation_id,)) as cur:
            neg = await cur.fetchone()
        if not neg:
            raise HTTPException(404, "Negotiation not found")
        async with db.execute("SELECT * FROM messages WHERE negotiation_id = ? ORDER BY created_at", (negotiation_id,)) as cur:
            messages = await cur.fetchall()
    return {"id": neg["id"], "family_id": neg["family_id"], "topic": neg["topic"], "status": neg["status"], "agreement": neg["final_agreement"], "transcript": [{"role": m["role"], "sender": m["sender"], "content": m["content"], "timestamp": m["created_at"]} for m in messages]}

@app.get("/families/{family_id}/negotiations")
async def list_negotiations(family_id: str):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT id, topic, status, final_agreement, created_at FROM negotiations WHERE family_id = ? ORDER BY created_at DESC", (family_id,)) as cur:
            rows = await cur.fetchall()
    return {"negotiations": [dict(r) for r in rows]}

@app.get("/health")
async def health():
    return {"status": "ok", "service": "CoParent AI"}