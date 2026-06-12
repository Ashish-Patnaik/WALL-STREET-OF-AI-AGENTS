import sqlite3

def init_db():
    conn = sqlite3.connect('venturepit.db', check_same_thread=False)
    c = conn.cursor()
    
    # Tables
    c.execute('CREATE TABLE IF NOT EXISTS agents (name TEXT, role TEXT, goal TEXT, cash INTEGER, location TEXT, speech TEXT, thought TEXT, action_id INTEGER)')
    c.execute('CREATE TABLE IF NOT EXISTS memories (tick INTEGER, agent TEXT, memory TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS news (tick INTEGER, headline TEXT)')
    
    # Initialize the 4 Traders with EQUAL STARTING CASH ($100,000)
    c.execute("SELECT count(*) FROM agents")
    if c.fetchone()[0] == 0:
        agents = [
            ("Alex", "Crypto Degenerate", "Find 100x moonshots.", 10000, "Startup Offices", "Let's trade!", "I need to win.", 0),
            ("Sarah", "Bear Market Shorter", "Protect capital and short.", 10000, "VC Office", "The market will crash.", "I'm playing it safe.", 0),
            ("Alice", "Quant Algo Trader", "Trade on tech data.", 10000, "Coffee Shop", "My algos are running.", "Data never lies.", 0),
            ("Mike", "Hype Trader", "Trade on breaking news.", 10000, "News Room", "Did you see the news?", "I hope I'm not too late.", 0)
        ]
        c.executemany("INSERT INTO agents VALUES (?, ?, ?, ?, ?, ?, ?, ?)", agents)
        c.execute("INSERT INTO news VALUES (0, '🚨 TRADING FLOOR OPEN: All agents start with $10,000.')")
        
    conn.commit()
    return conn

# Create a global connection pool
db_conn = init_db()