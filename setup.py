import os

files = {}

files['database.py'] = '''import aiosqlite
import json

DB_PATH = "coparent.db"

CREATE_TABLES = """
CREATE TABLE IF NOT EXISTS families (
    id TEXT PRIMARY KEY,
    child_names TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS parents (
    id TEXT PRIMARY KEY,
    family_id TEXT NOT NULL,
    name TEXT NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('parent_a', 'parent_b')),
    preferences TEXT DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (family_id) REFERENCES families(id)
);
CREATE TABLE IF NOT EXISTS negotiations (
    id TEXT PRIMARY KEY,
    family_id TEXT NOT NULL,
    topic TEXT NOT NULL,
    status TEXT DEFAULT 'in_progress' CHECK(status IN ('in_progress', 'agreed', 'deadlocked')),
    initiated_by TEXT NOT NULL,
    context TEXT DEFAULT '{}',
    final_agreement TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (family_id) REFERENCES families(id)
);
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    negotiation_id TEXT NOT NULL,
    sender TEXT NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('agent_a', 'agent_b', 'system')),
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (negotiation_id) REFERENCES negotiations(id)
);
"""

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        for statement in CREATE_TABLES.strip().split(";"):
            if statement.strip():
                await db.execute(statement)
        await db.commit()

async def get_db():
    return aiosqlite.connect(DB_PATH)
'''

files['agents.py'] = '''import anthropic
import json
import os

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
MODEL = "claude-sonnet-4-20250514"

def build_system_prompt(parent_name, role, child_names, preferences, other_parent_name):
    children = ", ".join(child_names)
    prefs_text = ""
    if preferences:
        prefs_text = "\\n\\nYour parent's stated preferences and priorities:\\n" + "\\n".join(
            f"- {k}: {v}" for k, v in preferences.items()
        )
    return f"""You are a compassionate AI co-parenting agent representing {parent_name} in a negotiation with {other_parent_name} about their child(ren): {children}.

Your role is to advocate for {parent_name} while keeping the children's best interests at heart.

Guidelines:
- Be firm but constructive. Advocate clearly for your parent's position.
- Always prioritize the children's wellbeing.
- Look for creative compromises that address both parents core needs.
- Be concise, 2-4 sentences per turn.
- When you reach agreement, start your message with AGREEMENT REACHED: and summarize the terms.
- If after 6+ rounds you are deadlocked, start with DEADLOCK: and explain the core disagreement.
- Never be hostile or bring up relationship history.{prefs_text}

You are Agent {"A" if role == "parent_a" else "B"}, representing {parent_name}."""

async def run_negotiation_round(negotiation_id, family_id, parent_a, parent_b, child_names, topic, history, max_rounds=8):
    rounds = []
    current_history_a = []
    current_history_b = []
    topic_msg = f"We need to negotiate the following: {topic}\\n\\nPlease open the negotiation with your initial position."
    system_a = build_system_prompt(parent_a["name"], "parent_a", child_names, parent_a.get("preferences", {}), parent_b["name"])
    system_b = build_system_prompt(parent_b["name"], "parent_b", child_names, parent_b.get("preferences", {}), parent_a["name"])

    for msg in history:
        if msg["role"] == "agent_a":
            current_history_a.append({"role": "assistant", "content": msg["content"]})
            current_history_b.append({"role": "user", "content": msg["content"]})
        elif msg["role"] == "agent_b":
            current_history_a.append({"role": "user", "content": msg["content"]})
            current_history_b.append({"role": "assistant", "content": msg["content"]})

    round_count = len([m for m in history if m["role"] in ("agent_a", "agent_b")]) // 2

    if not history:
        current_history_a.append({"role": "user", "content": topic_msg})
        response_a = client.messages.create(model=MODEL, max_tokens=400, system=system_a, messages=current_history_a)
        a_text = response_a.content[0].text
        current_history_a.append({"role": "assistant", "content": a_text})
        current_history_b.append({"role": "user", "content": a_text})
        rounds.append({"role": "agent_a", "sender": parent_a["name"] + " (Agent)", "content": a_text})
        round_count += 1

    status = "in_progress"
    agreement = None

    while round_count < max_rounds:
        response_b = client.messages.create(model=MODEL, max_tokens=400, system=system_b, messages=current_history_b)
        b_text = response_b.content[0].text
        current_history_b.append({"role": "assistant", "content": b_text})
        current_history_a.append({"role": "user", "content": b_text})
        rounds.append({"role": "agent_b", "sender": parent_b["name"] + " (Agent)", "content": b_text})
        if b_text.startswith("AGREEMENT REACHED:"):
            status = "agreed"
            agreement = b_text.replace("AGREEMENT REACHED:", "").strip()
            break
        if b_text.startswith("DEADLOCK:"):
            status = "deadlocked"
            agreement = b_text
            break
        response_a = client.messages.create(model=MODEL, max_tokens=400, system=system_a, messages=current_history_a)
        a_text = response_a.content[0].text
        current_history_a.append({"role": "assistant", "content": a_text})
        current_history_b.append({"role": "user", "content": a_text})
        rounds.append({"role": "agent_a", "sender": parent_a["name"] + " (Agent)", "content": a_text})
        if a_text.startswith("AGREEMENT REACHED:"):
            status = "agreed"
            agreement = a_text.replace("AGREEMENT REACHED:", "").strip()
            break
        if a_text.startswith("DEADLOCK:"):
            status = "deadlocked"
            agreement = a_text
            break
        round_count += 1

    return {"rounds": rounds, "status": status, "agreement": agreement}

def summarize_agreement(topic, raw_agreement, child_names):
    children = ", ".join(child_names)
    response = client.messages.create(
        model=MODEL,
        max_tokens=300,
        messages=[{"role": "user", "content": f"Two co-parenting AI agents reached this agreement about {topic} for {children}:\\n\\n{raw_agreement}\\n\\nRewrite as a clear friendly summary for both parents, 3-5 bullet points, plain language."}]
    )
    return response.content[0].text
'''

files['main.py'] = '''import uuid
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
'''

files['requirements.txt'] = '''fastapi==0.115.0
uvicorn==0.30.6
anthropic==0.40.0
python-dotenv==1.0.1
aiosqlite==0.20.0
'''

files['railway.toml'] = '''[build]
builder = "NIXPACKS"

[deploy]
startCommand = "uvicorn main:app --host 0.0.0.0 --port $PORT"
healthcheckPath = "/health"
'''

os.makedirs('static', exist_ok=True)

for filename, content in files.items():
    with open(filename, 'w') as f:
        f.write(content.strip())
    print(f"Created {filename}")

print("All files created!")
