import berserk
import chess
import chess.engine
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("LICHESS_TOKEN")
STOCKFISH_PATH = os.getenv("STOCKFISH_PATH")

session = berserk.TokenSession(TOKEN)
client = berserk.Client(session)

def get_best_move(fen, time_limit=0.1):
    board = chess.Board(fen)
    with chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH) as engine:
        result = engine.play(board, chess.engine.Limit(time=time_limit))
        return result.move.uci()

def handle_game(game_id):
    print(f"Partie lancée : {game_id}")
    board = chess.Board()
    
    for event in client.bots.stream_game_state(game_id):
        if event["type"] == "gameFull":
            moves = event["state"]["moves"].split()
            bot_color = "white" if event["white"].get("id") == "tanukichessbot" else "black"
        elif event["type"] == "gameState":
            moves = event["moves"].split()
        else:
            continue

        board = chess.Board()
        for move in moves:
            if move:
                board.push_uci(move)

        is_bot_turn = (board.turn == chess.WHITE and bot_color == "white") or \
                      (board.turn == chess.BLACK and bot_color == "black")

        if is_bot_turn and not board.is_game_over():
            move = get_best_move(board.fen())
            client.bots.make_move(game_id, move)
            print(f"Coup joué : {move}")

def main():
    print("TanukiChessBot démarré...")
    
    # Upgrade du compte en bot (une seule fois)
    try:
        client.bots.upgrade_to_bot()
        print("Compte upgradé en bot ✅")
    except:
        print("Déjà bot ✅")

    for event in client.bots.stream_incoming_events():
        if event["type"] == "challenge":
            challenge_id = event["challenge"]["id"]
            client.bots.accept_challenge(challenge_id)
            print(f"Défi accepté : {challenge_id}")
        elif event["type"] == "gameStart":
            handle_game(event["game"]["gameId"])

if __name__ == "__main__":
    main()