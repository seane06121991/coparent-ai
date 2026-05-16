import aiosqlite
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