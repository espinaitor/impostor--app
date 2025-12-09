from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, RedirectResponse
import secrets

app = FastAPI(title="El Impostor", version="1.0.0")

game_state = None

WORDS_AND_CLUES = [
    ("astronauta", "cohete"),
    ("chef", "cuchillo"),
    ("médico", "estetoscopio"),
    ("policía", "pistola"),
    ("profesor", "pizarra"),
    ("bombero", "manguera"),
    ("cantante", "micrófono"),
    ("pintor", "pincel"),
    ("detective", "lupa"),
    ("granjero", "tractor"),
    ("ninja", "shuriken"),
    ("pirata", "brújula"),
    ("espía", "disfraz"),
]

def get_base_html(content: str) -> str:
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>El Impostor</title>
        <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700&family=Exo+2:wght@400;600&display=swap" rel="stylesheet">
        <style>
            :root {{
                --bg: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
                --card: rgba(30, 30, 46, 0.85);
                --text: #e0e0ff;
                --impostor: #ff3b30;
                --crew: #4cd964;
                --button: #6a5acd;
                --button-hover: #8a7bf0;
                --reveal: #ff9500;
            }}
            * {{
                box-sizing: border-box;
                margin: 0;
                padding: 0;
            }}
            body {{
                font-family: 'Exo 2', sans-serif;
                background: var(--bg);
                background-attachment: fixed;
                color: var(--text);
                line-height: 1.6;
                padding: 20px;
                min-height: 100vh;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                text-align: center;
            }}
            h1, h2 {{
                font-family: 'Orbitron', monospace;
                margin: 16px 0;
                text-shadow: 0 0 10px rgba(100, 100, 255, 0.6);
            }}
            h1 {{
                font-size: 2.4rem;
                color: var(--crew);
            }}
            h2 {{
                font-size: 1.8rem;
            }}
            textarea {{
                width: 100%;
                height: 160px;
                padding: 16px;
                font-size: 1.1rem;
                border: 2px solid #5a5a8e;
                border-radius: 14px;
                background: rgba(20, 20, 35, 0.9);
                color: #ffffff;
                margin: 16px 0;
                resize: vertical;
                font-family: 'Exo 2', sans-serif;
            }}
            button {{
                width: 100%;
                padding: 16px;
                font-size: 1.25rem;
                font-weight: bold;
                font-family: 'Orbitron', monospace;
                border: none;
                border-radius: 14px;
                cursor: pointer;
                margin: 12px 0;
                transition: all 0.2s ease;
                letter-spacing: 1px;
            }}
            button:hover {{
                opacity: 0.9;
            }}
            button:active {{
                transform: scale(0.97);
            }}
            .btn-primary {{
                background: var(--button);
                color: white;
            }}
            .btn-reveal {{
                background: var(--reveal);
                color: #000;
            }}
            .btn-impostor {{
                background: var(--impostor);
                color: white;
            }}
            .card {{
                background: var(--card);
                padding: 24px;
                border-radius: 20px;
                margin: 20px 0;
                box-shadow: 0 8px 30px rgba(0, 0, 0, 0.5);
                backdrop-filter: blur(4px);
                border: 1px solid rgba(100, 100, 255, 0.2);
            }}
            .player-name {{
                font-family: 'Orbitron', monospace;
                font-size: 3.6rem;
                font-weight: 700;
                color: var(--impostor);
                margin: 20px 0;
                text-shadow: 0 0 20px rgba(255, 59, 48, 0.7);
                letter-spacing: -1px;
            }}
            #role {{
                font-size: 1.5rem;
                margin: 24px 0;
                padding: 18px;
                background: rgba(0,0,0,0.3);
                border-radius: 14px;
                display: none;
                border-left: 4px solid var(--crew);
            }}
            footer {{
                margin-top: 30px;
                color: #aaa;
                font-size: 0.85rem;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            {content}
        </div>
    </body>
    </html>
    """

@app.get("/", response_class=HTMLResponse)
def home():
    global game_state
    game_state = None
    content = """
    <h1>IMPOSTOR</h1>
    <div class="card">
        <p>Introduce los nombres de los participantes (uno por línea):</p>
        <form method="post" action="/setup">
            <textarea name="players" placeholder="Aitor\nJon\nMikel\n..."></textarea><br>
            <button type="submit" class="btn-primary">¡Empezar partida!</button>
        </form>
    </div>
    """
    return HTMLResponse(get_base_html(content))

@app.post("/setup")
def setup_game(players: str = Form(...)):
    global game_state
    player_list = [p.strip() for p in players.strip().splitlines() if p.strip()]
    if len(player_list) < 3:
        content = """
        <h1>⚠️ Error</h1>
        <div class="card">
            <p>Se necesitan al menos 3 jugadores.</p>
            <a href="/" style="display: block; margin-top: 16px; text-decoration: none;">
                <button class="btn-primary">← Volver</button>
            </a>
        </div>
        """
        return HTMLResponse(get_base_html(content), status_code=400)

    word, clue = secrets.choice(WORDS_AND_CLUES)
    impostor = secrets.choice(player_list)

    game_state = {
        "players": player_list,
        "word": word,
        "clue": clue,
        "impostor": impostor,
        "current_index": 0,
        "total": len(player_list),
    }
    return RedirectResponse(url="/show_role", status_code=303)

@app.get("/show_role", response_class=HTMLResponse)
def show_role():
    global game_state
    if not game_state:
        return RedirectResponse("/", status_code=303)

    if game_state["current_index"] >= game_state["total"]:
        starter = secrets.choice(game_state["players"])
        content = f"""
        <h1>✅ ¡Todos listos!</h1>
        <div class="card">
            <h2>🗣️ <u>{starter}</u> empieza a hablar.</h2>
            <p>¡Buena suerte a todos!</p>
            <form method="post" action="/reveal_impostor">
                <button type="submit" class="btn-impostor">👁️‍🗨️ Desvelar impostor</button>
            </form>
        </div>
        """
        return HTMLResponse(get_base_html(content))

    current_player = game_state["players"][game_state["current_index"]]
    is_impostor = (current_player == game_state["impostor"])
    secret_message = (
        f"¡Eres el <strong>IMPOSTOR</strong>! Tu pista es: <strong>{game_state['clue']}</strong>"
        if is_impostor else
        f"Tu palabra secreta es: <strong>{game_state['word']}</strong>"
    )

    content = f"""
    <div class="player-name">{current_player}</div>
    <div id="role">{secret_message}</div>
    <button id="reveal" class="btn-reveal" onclick="revealRole()">👁️ Desvelar rol</button>
    <form method="post" action="/next" style="display:none;" id="nextForm">
        <button type="submit" class="btn-primary">✅ Rol visto</button>
    </form>

    <script>
        function revealRole() {{
            document.getElementById('role').style.display = 'block';
            document.getElementById('reveal').style.display = 'none';
            document.getElementById('nextForm').style.display = 'block';
        }}
    </script>
    """
    return HTMLResponse(get_base_html(content))

@app.post("/next")
def next_player():
    global game_state
    if game_state:
        game_state["current_index"] += 1
    return RedirectResponse(url="/show_role", status_code=303)

@app.post("/reveal_impostor")
def reveal_impostor():
    global game_state
    impostor = game_state["impostor"] if game_state else "Desconocido"
    content = f"""
    <h1>🚨 ¡El impostor era...</h1>
    <div class="card">
        <h2 style="color: var(--impostor); font-size: 2.5rem;">{impostor}!</h2>
        <p style="margin-top: 20px;">Gracias por jugar.</p>
        <a href="/" style="display: block; margin-top: 20px; text-decoration: none;">
            <button class="btn-primary">↺ Nueva partida</button>
        </a>
    </div>
    """
    return HTMLResponse(get_base_html(content))

# === PARA LA NUBE ===
if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)