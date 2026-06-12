<div align="center">

<div align="center">

<img src="https://cdn-uploads.huggingface.co/production/uploads/679f1bd801f97ba49a8e81ec/Cmf3W6hEo_PwrBp2PmZSR.png" width="900">

</div>

<h1 align="center" style="font-size: 64px;">
🐺 WALL STREET OF AI AGENTS
</h1>

<h3><i>An autonomous trading firm run entirely by AI Agents.</i></h3>



[![Hackathon](https://img.shields.io/badge/Build_Small_Hackathon_2026-🍄_Thousand_Token_Wood-8B5CF6?style=for-the-badge)](https://huggingface.co/build-small-hackathon)
[![Model](https://img.shields.io/badge/Model-MiniCPM5_1B_GGUF-F97316?style=for-the-badge)](https://huggingface.co/openbmb/MiniCPM5-1B-GGUF)
[![Runtime](https://img.shields.io/badge/Runtime-llama.cpp-22C55E?style=for-the-badge)](#)
[![Agents](https://img.shields.io/badge/Agents-4_Autonomous_Traders-3B82F6?style=for-the-badge)](#)

**▶️ [Enter the Trading Floor (Live Space)](https://huggingface.co/spaces/build-small-hackathon/Wall-Street-of-AI-Agents) · 🎬 [Watch the Demo Video](https://youtu.be/1XZuUsiwuTA) · 📓 [Read the Build Log](#)**

</div>

---

![preview](https://cdn-uploads.huggingface.co/production/uploads/679f1bd801f97ba49a8e81ec/pWmQqMc9eFooLVXzn-fpf.webp)

> *Sarah leads the leaderboard at $10,700. Alice is arguing with Mike in the hallway. Alex is alone in the Office. The market is Stagnant. Panic ensues.*

---

## 📈 The Vision: A Game & A Benchmark

Most AI agent frameworks are built for B2B tasks—writing code, scraping data, summarizing emails. We wanted to build something weird, delightful, and highly voyeuristic. 

**Wall St. of Agents** is a high-frequency trading reality show. Four AI agents, each with a distinct personality and financial strategy, wander a pixel-art office, overhear each other, and make real trades—continuously, forever, without a single human input.

But beneath the retro 2D graphics lies something much more ambitious: **a visual benchmark for testing multi-agent collaboration and LLM reasoning.** 
By trapping a tiny 1-Billion parameter model in a dynamic financial simulation, we can stress-test its capabilities live:
* **Strict Instruction Following:** Can the model adhere to a rigid JSON schema while adopting a complex persona?
* **Regime Adaptation:** When the market shifts from a *Tech Boom* to a *Market Crash*, does the model adjust its trading strategy, or does it stubbornly hold?
* **Spatially-Aware Social Dynamics:** Can agents hold a logical conversation based *only* on who is physically standing in the same room as them?

---

## 👔 The Four Agents

Four traders. Four worldviews. One shared office where they cannot stop running into each other. Every agent starts with **$10,000**.


---
<table>
<tr>

<td width="25%" align="center">
<img src="dist/assets/faces/Alex.png" width="140" alt="Alex"><br>
<h3>💎 Alex</h3>
<b>The Crypto Degen</b><br>
<i>Reckless. Infectious. Convinced every regime is secretly a bull run. Will talk anyone into a bad trade with sheer confidence. Thrives in Crypto Frenzies. Obliterated in crashes.</i>
</td>

<td width="25%" align="center">
<img src="dist/assets/faces/Sarah.png" width="140" alt="Sarah"><br>
<h3>🧊 Sarah</h3>
<b>Bear Market Shorter</b><br>
<i>Cynical. Precise. Has been waiting for the market to collapse since tick one. Quietly holds bonds while everyone else panics. Weirdly calm when it all falls apart.</i>
</td>

<td width="25%" align="center">
<img src="dist/assets/faces/Alice.png" width="140" alt="Alice"><br>
<h3>📊 Alice</h3>
<b>Quant Algo Trader</b><br>
<i>Cold. Methodical. Speaks in probabilities. Ignores breaking news unless it clears her signal threshold. Consistently the most rational agent in any room she walks into.</i>
</td>

<td width="25%" align="center">
<img src="dist/assets/faces/Mike.png" width="140" alt="Mike"><br>
<h3>📰 Mike</h3>
<b>The Hype Trader</b><br>
<i>Anxious. Always three minutes late to the trade. Buys the top, panics at the bottom, blames the headline. The most entertaining agent to watch during a market crash.</i>
</td>

</tr>
</table>

---

## 🧠 Lightweight Agentic Architecture

Traditional multi-agent frameworks (like AutoGen or CrewAI) are notoriously heavy and slow. We built a hyper-lightweight, spatially-aware architecture tailored specifically for edge computing and small GGUF models.

### 1. Spatial Collaboration (No Message Bus Required)
No orchestration layer. No shared memory pool. **Physical proximity drives conversation.** 
Before every agent's turn, the Python engine queries the SQLite database for physical room occupancy:
```python
c.execute("SELECT name, speech FROM agents WHERE location=? AND name!=?", (location, name))
```
If Alex and Sarah are both in the VC Office, Sarah's last spoken line gets injected directly into Alex's local prompt with a hard instruction:
> *"Sarah is here. She just said: 'Hold cash for safety.' INSTRUCTION: Reply directly to what she said."*

### 2. The Financial Evaluation Engine
The simulation models four distinct market regimes. Each one rewards different strategies and punishes others. 
* 🚀 **Crypto Frenzy:** Crypto (+$3,500) | Bonds (−$800)
* 💀 **Market Crash:** Bonds (+$1,500) | Crypto (−$4,000)

Watch a 40-tick simulation and you'll see genuine portfolio divergence driven entirely by personality—not luck, not RNG, but the model's consistent interpretation of four different personas under pressure.

### 3. The ⚡ TRIGGER CHAOS Button
One button. No text box. No prompt engineering required from the user.
Hit it, and the system auto-generates a breaking news headline, injects it into the shared news feed, and flips the market state to `MARKET CRASH`. Every agent reads the same event through their own filter. Sarah smiles and rebalances. Mike screams and panic-sells. 

---

## 🛠️ The Technical Core (Bulletproof 1B Inference)

Running a continuous multi-agent loop on a Free CPU Space is incredibly difficult. Small models hallucinate. They add markdown. They write *"Sure! Here's your trading decision:"* before the JSON. Every one of these quirks crashes a standard game loop.

**We don't sanitize in Python. We prevent it in C++ at the token sampling level.**

Leveraging `llama-cpp-python`'s Native JSON Schema feature, we hook into the logit generation process. The model is **physically prevented** from choosing tokens that violate our game's API structure:
```python
response_format={
    "type": "json_object",
    "schema": {
        "type": "object",
        "properties": {
            "trade": {"type": "string", "enum": ["Tech", "Crypto", "Bonds", "Hold"]},
            "speech": {"type": "string"},
            "thought": {"type": "string"},
            "location": {"type": "string", "enum": ["Startup Offices", "VC Office", "Coffee Shop", "News Room"]}
        },
        "required": ["trade", "speech", "thought", "location"]
    }
}
```
This constraint makes the `MiniCPM5-1B` punch *massively* above its weight class. It runs cleanly on a 2-vCPU Hugging Face Space—or flies at lightning speed if it auto-detects a local GPU—without ever crashing the game loop.

---

## 🎨 The UI: This Is Gradio. You'd Never Know.

We completely bypassed the stock Gradio chat-interface to build a stunning, Neubrutalist financial dashboard using `gr.HTML` injection.

* **Live Leaderboard (Left):** Agent portraits, current cash, and locations. Watch the rankings shift in real-time.
* **The Trading Floor (Center):** A custom **Phaser.js** 2D game engine. Agent sprites have walk animations, anti-stuck pathfinding, and dynamic speech bubbles.
* **Dual Timelines (Right):** The UI intelligently parses the database, sending Macro Market shifts to the **World Timeline**, and real-time agent conversations to the **Trading Floor Timeline**.
* **The Confession Booth (Right):** Because the model outputs a structured payload, we split their public `"speech"` from their private `"thought"`. Clicking an agent's sprite reveals their hidden anxieties, exposing the reasoning model's inner monologue while they publicly project confidence.

---

## 🏅 Badges Claimed

| Badge | The Case |
|---|---|
| 🍄 **Thousand Token Wood** | A weird, delightful, voyeuristic simulation. The AI doesn't help you build the game; the AI *is* the game. |
| 🔌 **Off the Grid** | Zero cloud APIs. `n_gpu_layers=0` gracefully falls back to CPU. The entire firm runs in RAM. |
| 🦙 **Llama Champion** | Raw `llama-cpp-python` runtime. JSON Schema enforcement at the C++ logit layer is load-bearing. |
| 🎨 **Off-Brand** | Phaser.js + custom CSS injected via FastAPI into Gradio. You wouldn't know it's Gradio. |
| 🐜 **Tiny Titan** | 1B params. Q4 quantized. 2 vCPUs. 4 simultaneous autonomous agents. Continuous uptime. |
| 🏮 **OpenBMB** | `MiniCPM5-1B-GGUF` isn't a fallback—it's the entire cognitive brain of the operation. |

---

## 💻 Run It Locally

No API keys. No `.env` files required. 
```bash
git clone https://huggingface.co/spaces/YOUR_USERNAME/Wall-Street-of-AI-Agents
cd Wall-Street-of-AI-Agents

pip install -r requirements.txt

# Download MiniCPM-1B-sft-q4_0.gguf from HuggingFace and place it in /models/

python app.py
```
*The trading floor opens at `http://localhost:7860`.*

---

## 🙏 Credits

* **[OpenBMB](https://huggingface.co/openbmb)** — `MiniCPM5-1B` is the entire cognitive layer of this firm.
* **[llama.cpp](https://github.com/ggerganov/llama.cpp)** — The runtime that makes CPU-only multi-agent simulation viable and fast.
* **[Phaser.js](https://phaser.io)** — The 2D HTML5 engine living inside the Gradio iframe.
* **[Hugging Face](https://huggingface.co)** — Docker Spaces and the hackathon that brought this to life.

<div align="center">
<br>
<i>Four agents. One model. No cloud. No mercy.</i><br>
<b>📉 The market doesn't care about your architecture choices. 📈</b>
</div>
