import gradio as gr
import threading
import time
import random
import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from contextlib import asynccontextmanager
from db import db_conn, init_db
from engine import run_agent_turn

world_state = {"market_condition": "Stagnant Market", "tick": 1}

# ─────────────────────────────────────────
# 1. The Autonomous AI Loop
# ─────────────────────────────────────────
def simulation_loop():
    print("🧠 Trading Floor Booted Up!")
    while True:
        if world_state["tick"] > 0 and world_state["tick"] % 2 == 0:
            possible_markets = ["Tech Boom", "Crypto Frenzy", "Stagnant Market"]
            if world_state["market_condition"] in possible_markets:
                possible_markets.remove(world_state["market_condition"])
            world_state["market_condition"] = random.choice(possible_markets)
            c = db_conn.cursor()
            c.execute("INSERT INTO news VALUES (?, ?)", (world_state["tick"], f"🌍 GLOBAL MARKET SHIFT: {world_state['market_condition']}"))
            db_conn.commit()
        run_agent_turn(world_state["tick"], world_state["market_condition"])
        world_state["tick"] += 1
        time.sleep(4)

# ─────────────────────────────────────────
# 2. Background thread — don't freeze FastAPI
# ─────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    thread = threading.Thread(target=simulation_loop, daemon=True)
    thread.start()
    yield

app = FastAPI(lifespan=lifespan)

class ChaosEvent(BaseModel):
    headline: str

@app.get("/api/state")
def get_state():
    c = db_conn.cursor()
    c.execute("SELECT name, location, speech, thought, action_id, cash FROM agents")
    agents = {row[0]: {
        "location": row[1],
        "speech": row[2],
        "private_thought": row[3],
        "action_id": row[4],
        "cash": row[5]
    } for row in c.fetchall()}
    c.execute("SELECT headline FROM news ORDER BY tick DESC LIMIT 10")
    news_feed = [row[0] for row in c.fetchall()]
    return {
        "agents": agents,
        "news_feed": list(reversed(news_feed)),
        "market_condition": world_state["market_condition"]
    }

@app.post("/api/chaos")
def trigger_chaos(event: ChaosEvent):
    world_state["market_condition"] = "Market Crash"
    c = db_conn.cursor()
    c.execute("INSERT INTO news VALUES (?, ?)", (world_state["tick"], f"🚨 BREAKING: {event.headline} MARKET CRASH! 🚨"))
    db_conn.commit()
    return {"status": "Chaos injected"}

app.mount("/static", StaticFiles(directory="dist"), name="static")

# ─────────────────────────────────────────
# 3. CSS — neubrutalism, cozy palette, game gets FULL width
# ─────────────────────────────────────────
css = """
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700;800&family=Space+Mono:wght@400;700&display=swap');

:root {
    --cream:    #FDF6EC;
    --warm:     #F5E6C8;
    --honey:    #E8C87A;
    --rust:     #C94F2C;
    --forest:   #2D5016;
    --ink:      #1A1A1A;
    --card-bg:  #FFFBF3;
    --shadow:   4px 4px 0px #1A1A1A;
    --shadow-lg:6px 6px 0px #1A1A1A;
}

/* ── Gradio reset ── */
.gradio-container {
    max-width: 100% !important;
    padding: 0 !important;
    margin: 0 !important;
    background: var(--cream) !important;
    font-family: 'Space Grotesk', sans-serif !important;
}
footer { display: none !important; }
.main  { padding: 0 !important; }
div.svelte-byatnx { padding: 0 !important; }

/* ── Header ── */
.neu-header {
    background: var(--ink);
    border-bottom: 4px solid var(--honey);
    padding: 16px 32px;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-direction: column;
    gap: 4px;
    text-align: center;
}
.neu-header h1 {
    font-family: 'Space Mono', monospace;
    font-size: 2rem;
    font-weight: 700;
    color: var(--honey);
    letter-spacing: 2px;
    margin: 0;
    line-height: 1;
}
.neu-header .tagline {
    font-size: 0.7rem;
    color: #999;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    font-family: 'Space Mono', monospace;
}

/* ── Scrolling ticker ── */
.ticker-wrap {
    background: var(--rust);
    border-bottom: 3px solid var(--ink);
    overflow: hidden;
    padding: 5px 0;
}
.ticker-track {
    display: inline-block;
    white-space: nowrap;
    animation: ticker 28s linear infinite;
    color: #fff;
    font-family: 'Space Mono', monospace;
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.06em;
}
@keyframes ticker {
    0%   { transform: translateX(100vw); }
    100% { transform: translateX(-100%); }
}

/* ── Status bar (market + tick) ── */
.status-bar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 10px 20px;
    background: var(--warm);
    border-bottom: 2.5px solid var(--ink);
}
.market-badge {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: var(--honey);
    color: var(--ink);
    border: 2.5px solid var(--ink);
    box-shadow: var(--shadow);
    font-family: 'Space Mono', monospace;
    font-size: 0.82rem;
    font-weight: 700;
    padding: 5px 16px;
    letter-spacing: 0.04em;
}
.tick-pill {
    font-family: 'Space Mono', monospace;
    font-size: 0.7rem;
    color: #555;
    background: var(--card-bg);
    border: 2px solid var(--ink);
    padding: 4px 12px;
    letter-spacing: 0.1em;
}

/* ── GAME ZONE — full width, untouched ── */
.game-zone {
    width: 100%;
    background: #111;
    border-bottom: 3px solid var(--ink);
    line-height: 0;
}
.game-zone iframe {
    display: block;
    width: 100%;
    height: 560px;
    border: none;
}

/* ── Responsive ── */
@media (max-width: 900px) {
    .dash-row { grid-template-columns: 1fr; }
    .dash-col { border-right: none; border-bottom: 2.5px solid var(--ink); }
    .game-zone iframe { height: 420px; }
    .neu-header h1 { font-size: 1.4rem; }
}
"""

# ─────────────────────────────────────────
# 4. HTML — game full-width on top, 3-col dash below
# ─────────────────────────────────────────
custom_html = """
<!-- ── HEADER ── -->
<div class="neu-header">
    <h1>🐺 WALL STREET OF AI AGENTS</h1>
    <span class="tagline">A Multi AI Agent Trading Firm &nbsp;·&nbsp; Fully Autonomous Ecosystem Powered by Small Models</span>
</div>

<!-- ── SCROLLING TICKER ── -->
<div class="ticker-wrap">
    <span class="ticker-track">
        ◆ LIVE FEED &nbsp;·&nbsp; AI AGENTS TRADING IN REAL-TIME &nbsp;·&nbsp;
        DYNAMIC MARKET REGIMES &nbsp;·&nbsp;
        NO CLOUD APIS, JUST CHAOS &nbsp;·&nbsp;
        CLICK [TRIGGER CHAOS] TO LIQUIDATE THE SHORTS &nbsp;·&nbsp;
        POWERED BY MINICPM-1B + LLAMA.CPP &nbsp;·&nbsp;
        WATCH THEM PANIC IN REAL-TIME &nbsp;·&nbsp;
        4 AUTONOMOUS TRADERS COMPETE FOR PROFITS &nbsp;·&nbsp; ONLY THE BOLD SURVIVE &nbsp;◆
        &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
        ◆ LIVE FEED &nbsp;·&nbsp; AI AGENTS TRADING IN REAL-TIME &nbsp;·&nbsp;
        DYNAMIC MARKET REGIMES &nbsp;·&nbsp;
        NO CLOUD APIS, JUST CHAOS &nbsp;·&nbsp;
        CLICK [TRIGGER CHAOS] TO LIQUIDATE THE SHORTS &nbsp;·&nbsp;
        POWERED BY MINICPM-1B + LLAMA.CPP &nbsp;·&nbsp;
        WATCH THEM PANIC IN REAL-TIME &nbsp;·&nbsp;
        4 AUTONOMOUS TRADERS COMPETE FOR PROFITS &nbsp;·&nbsp; ONLY THE BOLD SURVIVE &nbsp;◆
    </span>
</div>

<!-- ── STATUS BAR ── -->
<div class="status-bar">
    <span class="market-badge" id="market-badge">📊 Loading market…</span>
    <span class="tick-pill" id="tick-display">TICK —</span>
</div>

<!-- ── PHASER GAME — full width, no sidebar ── -->
<div class="game-zone">
    <iframe
        src="/static/index.html"
        width="100%"
        height="560"
        frameborder="0"
        scrolling="no"
    ></iframe>
</div>



<script>
let tick = 0;

async function fetchState() {
    try {
        const res  = await fetch('/api/state');
        const data = await res.json();

        // Market badge
        const badge = document.getElementById('market-badge');
        if (badge) badge.textContent = '📊 ' + data.market_condition;

        // Tick
        tick++;
        const td = document.getElementById('tick-display');
        if (td) td.textContent = 'TICK ' + tick;

    } catch(e) { console.warn('State fetch failed', e); }
}

fetchState();
setInterval(fetchState, 4000);
</script>
"""

# ─────────────────────────────────────────
# 5. Gradio app
# ─────────────────────────────────────────
with gr.Blocks(title="Wall St. of Agents", css=css) as demo:
    gr.HTML(custom_html)

app = gr.mount_gradio_app(app, demo, path="/", theme=gr.themes.Base(), css=css)

# ─────────────────────────────────────────
# 6. Entry point
# ─────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    try:
        c = db_conn.cursor()
        c.execute("DROP TABLE IF EXISTS agents")
        c.execute("DROP TABLE IF EXISTS memories")
        c.execute("DROP TABLE IF EXISTS news")
        db_conn.commit()
        init_db()
        print("✅ Database successfully reset for new Game!")
    except Exception as e:
        print(f"Failed to reset DB: {e}")

    uvicorn.run(app, host="0.0.0.0", port=7860)