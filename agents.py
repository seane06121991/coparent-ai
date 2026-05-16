import anthropic
import json
import os

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
MODEL = "claude-sonnet-4-20250514"

def build_system_prompt(parent_name, role, child_names, preferences, other_parent_name):
    children = ", ".join(child_names)
    prefs_text = ""
    if preferences:
        prefs_text = "\n\nYour parent's stated preferences and priorities:\n" + "\n".join(
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
    topic_msg = f"We need to negotiate the following: {topic}\n\nPlease open the negotiation with your initial position."
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
        messages=[{"role": "user", "content": f"Two co-parenting AI agents reached this agreement about {topic} for {children}:\n\n{raw_agreement}\n\nRewrite as a clear friendly summary for both parents, 3-5 bullet points, plain language."}]
    )
    return response.content[0].text