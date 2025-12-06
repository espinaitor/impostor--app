from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, RedirectResponse
import secrets

app = FastAPI(title="IMPOSTOR", version="1.0.0")

# Estado de la partida (una sola partida a la vez)
game_state = None

# Palabras y pistas: (palabra_real, pista_para_impostor)
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
    ("piloto", "avión"),
    ("mecánico", "llave"),
    ("fotógrafo", "cámara"),
    ("actor", "guión"),
    ("científico", "microscopio"),
]

@app.get("/", response_class=HTMLResponse)
def home():
    global game_state
    game_state = None
    return HTMLResponse("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>IMPOSTOR</title>
        <meta charset="utf-8">
        <style>
            body { font-family: Arial, sans-serif; text-align: center; padding: 40px; background: #f0f0f0; }
            textarea { width: 90%; max-width: 400px; height: 150px; padding: 10px; font-size: 16px; }
            button { padding: 12px 24px; font-size: 18px; background: #1976d2; color: white; border: none; border-radius: 6px; cursor: pointer; }
            button:hover { background: #1565c0; }
        </style>
    </head>
    <body>
        <h1>🎨 El Impostor</h1>
        <p>Introduce los nombres de los participantes (uno por línea):</p>
        <form method="post" action="/setup">
            <textarea name="players" placeholder="Aitor\nMaría\nCarlos\n..."></textarea><br><br>
            <button type="submit">¡Empezar partida!</button>
        </form>
    </body>
    </html>
    """)

@app.post("/setup")
def setup_game(players: str = Form(...)):
    global game_state
    player_list = [p.strip() for p in players.strip().splitlines() if p.strip()]
    if len(player_list) < 3:
        return HTMLResponse(
            "<h2 style='text-align:center;color:red;'>Se necesitan al menos 3 jugadores.</h2>"
            "<p style='text-align:center;'><a href='/' style='color:blue;'>Volver</a></p>",
            status_code=400
        )

    # ✨ Aleatoriedad de alta calidad
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
        starter = game_state["players"][0]
        return HTMLResponse(f"""
        <!DOCTYPE html>
        <html>
        <head><title>¡A JUGAR!</title><meta charset="utf-8"></head>
        <body style="font-family:Arial;text-align:center;padding:50px;background:#e6f7ff;">
            <h1>✅ ¡Todos han visto su rol!</h1>
            <h2>🗣️ <u>{starter}</u> empieza a hablar.</h2>
            <p>¡Buena suerte a todos!</p>
            <form method="post" action="/reveal_impostor" style="margin-top:30px;">
                <button type="submit" style="padding:12px 24px;font-size:18px;background:#e53935;color:white;border:none;border-radius:6px;cursor:pointer;">
                    👁️‍🗨️ Desvelar impostor
                </button>
            </form>
        </body>
        </html>
        """)

    current_player = game_state["players"][game_state["current_index"]]
    is_impostor = (current_player == game_state["impostor"])
    secret_message = (
        f"¡Eres el IMPOSTOR! Tu pista es: <strong>{game_state['clue']}</strong>"
        if is_impostor else
        f"Tu palabra secreta es: <strong>{game_state['word']}</strong>"
    )

    return HTMLResponse(f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>{current_player}</title>
        <meta charset="utf-8">
        <style>
            body {{
                font-family: Arial, sans-serif;
                text-align: center;
                padding: 60px;
                background: #fff9c4;
            }}
            h1 {{
                font-size: 60px;
                color: #d32f2f;
                margin-bottom: 30px;
            }}
            #role {{
                font-size: 30px;
                margin: 30px 0;
                padding: 20px;
                background: white;
                border-radius: 12px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                display: none;
            }}
            button {{
                padding: 15px 30px;
                font-size: 20px;
                border: none;
                border-radius: 8px;
                cursor: pointer;
                margin: 10px;
            }}
            #reveal {{
                background: #ff9800;
                color: white;
            }}
            #next {{
                background: #4caf50;
                color: white;
                display: none;
            }}
        </style>
    </head>
    <body>
        <h1>{current_player}</h1>
        <div id="role">{secret_message}</div>

        <button id="reveal" onclick="revealRole()">👁️ Desvelar rol</button>
        <form id="nextForm" method="post" action="/next" style="display:inline;">
            <button id="next" type="submit">✅ Rol visto</button>
        </form>

        <script>
            function revealRole() {{
                document.getElementById('role').style.display = 'inline-block';
                document.getElementById('reveal').style.display = 'none';
                document.getElementById('next').style.display = 'inline-block';
            }}
        </script>
    </body>
    </html>
    """)

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
    return HTMLResponse(f"""
    <!DOCTYPE html>
    <html>
    <head><title>👁️ Impostor revelado</title><meta charset="utf-8"></head>
    <body style="font-family:Arial;text-align:center;padding:60px;background:#ffebee;color:#c62828;">
        <h1>🚨 ¡El impostor era...</h1>
        <h2 style="font-size:48px;">{impostor}!</h2>
        <p style="font-size:20px;margin-top:30px;">Gracias por jugar.</p>
        <a href="/" style="display:inline-block;margin-top:20px;padding:12px 24px;background:#1976d2;color:white;text-decoration:none;border-radius:6px;font-size:18px;">
            ↺ Nueva partida
        </a>
    </body>
    </html>
    """)


# === PARA EJECUCIÓN EN LA NUBE (Railway, Render, etc.) ===
if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)