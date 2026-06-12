import os
import json
import random
from llama_cpp import Llama
from db import db_conn


# print("Loading Local GGUF Model... Checking hardware...")
# MODEL_PATH = "./models/model.gguf"
REPO_ID = "AaryanK/Qwen3.5-2B-GGUF"
FILENAME = "*q4_k_m.gguf"

try:
    # TRY GPU FIRST: n_gpu_layers=-1 offloads all math to the Graphics Card
    llm = Llama.from_pretrained(
        repo_id=REPO_ID,
        filename=FILENAME,
        n_ctx=1024,   
        n_threads=4,
        n_gpu_layers=-1, # 🚀 AUTO-DETECT GPU!
        verbose=False 
    )
    print("✅ Local Model Loaded! (🚀 GPU ACCELERATION ENABLED)")
except Exception as e:
    print(f"⚠️ GPU offload failed or unsupported. Falling back to CPU... ({e})")
    # FALLBACK TO CPU ONLY
    llm = Llama.from_pretrained(
        repo_id=REPO_ID,
        filename=FILENAME,
        n_ctx=1024,   
        n_threads=4,
        n_gpu_layers=0,  # 🐌 CPU ONLY
        verbose=False 
    )
    print("✅ Local Model Loaded! (🐌 CPU MODE)")

LOCATIONS = ["Startup Offices", "VC Office", "Coffee Shop", "News Room"]

def run_agent_turn(tick, current_market):
    c = db_conn.cursor()
    c.execute("SELECT name, role, goal, cash, location FROM agents")
    agents = c.fetchall()
    
    c.execute("SELECT headline FROM news ORDER BY tick DESC LIMIT 4")
    recent_news = " | ".join([row[0] for row in c.fetchall()])
    
    for agent in agents:
        name, role, goal, cash, location = agent
        
        c.execute("SELECT name, speech FROM agents WHERE location=? AND name!=?", (location, name))
        others_in_room = c.fetchall()
        
        room_context = f"You are at the {location}."
        if others_in_room:
            room_context += " Also here right now:\n"
            for other_name, other_speech in others_in_room:
                room_context += f"- {other_name} just said: '{other_speech}'\n"
            room_context += "INSTRUCTION: Reply directly to what they said!"
        else:
            room_context += " You are alone."

        system_prompt = f"You are {name}, a {role}. Goal: {goal}. Cash: ${cash:,}. NEVER say you are an AI. You are a real trader."
        
        user_prompt = f"""{room_context}
GLOBAL MARKET: {current_market}
News: {recent_news}

Make a trading decision. Keep your "speech" under 10 words!"""

        try:
            response = llm.create_chat_completion(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
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
                        "required": ["trade", "speech", "thought", "location"],
                    },
                },
                temperature=0.8,
                max_tokens=60, # 🔴 FASTER GENERATION: Forces the CPU to stop calculating sooner!
            )
            
            content = response['choices'][0]['message']['content']
            
            # 🔴 CRITICAL FIX: Clean the string! 
            # 1B models often hallucinate raw \n or \t characters which crash json.loads.
            content = content.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
            
            # strict=False allows Python to be forgiving if the JSON is slightly malformed
            decision = json.loads(content, strict=False)
            
            new_loc = decision.get("location", location)
            if new_loc not in LOCATIONS: new_loc = location
                
            speech = decision.get("speech", "Checking the charts.")
            thought = decision.get("thought", "...")
            trade = decision.get("trade", "Hold").capitalize()

            cash_change = 0
            if current_market == "Tech Boom":
                if trade == "Tech": cash_change = 1800
                elif trade == "Crypto": cash_change = 200
                elif trade == "Bonds": cash_change = -500
            elif current_market == "Crypto Frenzy":
                if trade == "Crypto": cash_change = 3500
                elif trade == "Tech": cash_change = -500
                elif trade == "Bonds": cash_change = -800
            elif current_market == "Market Crash": 
                if trade == "Bonds": cash_change = 1500 
                elif trade == "Crypto": cash_change = -4000 
                elif trade == "Tech": cash_change = -2500
            else: # Stagnant Market
                if trade == "Hold": cash_change = 100
                else: cash_change = -200 
                
            new_cash = max(0, cash + cash_change)
            
            trend = "📈" if new_cash > cash else "📉" if new_cash < cash else "💬"
            trade_text = f"[{trade}]" if trade != "Hold" else ""
            log_message = f"{trend} {name} {trade_text}: '{speech}' [${new_cash:,}]"
            
        except Exception as e:
            print(f"Local Inference Error for {name}: {e}")
            
            # 🔴 FIX THE "FREEZING" SPRITE: 
            # If the AI errors out, force the character to walk to a DIFFERENT room!
            # This guarantees the game keeps moving and never looks stuck.
            available_locs = [l for l in LOCATIONS if l != location]
            new_loc = random.choice(available_locs)
            
            speech = "Let me check the other room."
            thought = "Market is too noisy right now."
            new_cash = cash
            trade = "Hold" 
            log_message = f"💬 {name} [Hold]: '{speech}' [${cash:,}]"

        # Update Database
        c.execute("UPDATE agents SET location=?, speech=?, thought=?, cash=?, action_id=action_id+1 WHERE name=?", 
                  (new_loc, speech, thought, new_cash, name))
        c.execute("INSERT INTO memories VALUES (?, ?, ?)", (tick, name, f"I traded {trade}, said '{speech}', and have ${new_cash:,}"))
        c.execute("INSERT INTO news VALUES (?, ?)", (tick, log_message))
        db_conn.commit()
        
        print(log_message)