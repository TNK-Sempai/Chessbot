import berserk
import chess
import chess.engine
import threading
import random
import time
import server
import pub
from bot.commentary import generate_commentary
from bot.voice import speak
from bot.twitch_chat import start_twitch_bot, pop_queue
from bot.stats import record_result, get_score_text
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("LICHESS_TOKEN")
STOCKFISH_PATH = os.getenv("STOCKFISH_PATH")

session = berserk.TokenSession(TOKEN)
client = berserk.Client(session)

current_game_id = None

def get_best_move(fen, time_limit=0.1):
    board = chess.Board(fen)
    with chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH) as engine:
        result = engine.play(board, chess.engine.Limit(time=time_limit))
        return result.move.uci()

def handle_game(game_id):
    global current_game_id
    current_game_id = game_id
    print(f"Partie lancée : {game_id}")
    board = chess.Board()
    bot_color = "white"
    game_over = False
    move_count = 0

    try:
        for event in client.bots.stream_game_state(game_id):
            if event["type"] == "gameFull":
                moves = event["state"]["moves"].split()
                bot_color = "white" if event["white"].get("id") == "tanukichessbot" else "black"
            elif event["type"] == "gameState":
                moves = event["moves"].split()
            else:
                continue

            board = chess.Board()
            for m in moves:
                if m:
                    board.push_uci(m)

            if board.is_game_over():
                game_over = True
                result = board.result()
                stats = record_result(result, bot_color)
                score_text = get_score_text()
                print(f"Partie terminée : {result} | {score_text}")

                def announce_end(r=result, bc=bot_color, st=score_text):
                    if r == "1-0":
                        msg = "The Tanuki wins. As expected." if bc == "white" else "Impressive. The Tanuki acknowledges your skill."
                    elif r == "0-1":
                        msg = "The Tanuki wins. As expected." if bc == "black" else "Interesting. The Tanuki will remember this."
                    else:
                        msg = "A draw. The Tanuki is generous today."
                    speak(msg)
                    time.sleep(3)
                    speak(st)
                threading.Thread(target=announce_end, daemon=True).start()
                break

            is_bot_turn = (board.turn == chess.WHITE and bot_color == "white") or \
                          (board.turn == chess.BLACK and bot_color == "black")

            if is_bot_turn and not board.is_game_over():
                move_uci = get_best_move(board.fen())
                move_obj = chess.Move.from_uci(move_uci)
                move_count += 1

                client.bots.make_move(game_id, move_uci)
                print(f"Coup joué : {move_uci}")

                if move_count % 3 == 0:
                    def comment_and_speak(b=board, m=move_obj, go_flag=lambda: game_over):
                        if go_flag():
                            return
                        commentary = generate_commentary(b, m)
                        if go_flag():
                            return
                        print(f"Commentaire : {commentary}")
                        speak(commentary)
                    threading.Thread(target=comment_and_speak, daemon=True).start()
                    
    except Exception as e:
        print(f"Partie interrompue : {e}")

    current_game_id = None

def challenge_next_in_queue():
    time.sleep(10)
    opponent = pop_queue()
    if not opponent:
        bots = ["maia1", "maia5", "maia9"]
        opponent = random.choice(bots)
        print(f"File vide — défi automatique contre {opponent}")
        speak(f"No challengers. The Tanuki challenges {opponent}.")
    else:
        print(f"Défi lancé contre {opponent} (file d'attente)")
        speak(f"Next challenger: {opponent}. Prepare yourself.")
    
    try:
        client.challenges.create(
            username=opponent,
            rated=False,
            clock_limit=600,
            clock_increment=5,
            color="random"
        )
    except Exception as e:
        print(f"Erreur défi : {e}")

def main():
    print("TanukiChessBot démarré...")

    try:
        client.bots.upgrade_to_bot()
        print("Compte upgradé en bot ✅")
    except:
        print("Déjà bot ✅")

    threading.Thread(target=start_twitch_bot, daemon=True).start()
    print("Chat Twitch lancé ✅")

    threading.Thread(target=challenge_next_in_queue, daemon=True).start()

    while True:
        try:
            for event in client.bots.stream_incoming_events():
                if event["type"] == "challenge":
                    challenge_id = event["challenge"]["id"]
                    try:
                        client.bots.accept_challenge(challenge_id)
                        print(f"Défi accepté : {challenge_id}")
                    except Exception as e:
                        print(f"Défi expiré : {challenge_id}")
                elif event["type"] == "gameStart":
                    handle_game(event["game"]["gameId"])
                    threading.Thread(target=challenge_next_in_queue, daemon=True).start()
        except Exception as e:
            print(f"Connexion perdue, reconnexion dans 5s... {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()