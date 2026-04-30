import ollama
import chess
import random

client = ollama.Client(host="http://192.168.129.47:11434")

# Anti-répétition — garde les 5 derniers commentaires
_recent_comments = []

def get_position_context(board: chess.Board, move: chess.Move) -> str:
    context = []

    # Matériel
    piece_values = {chess.PAWN: 1, chess.KNIGHT: 3, chess.BISHOP: 3, chess.ROOK: 5, chess.QUEEN: 9}
    white_material = sum(piece_values.get(p.piece_type, 0) for p in board.piece_map().values() if p.color == chess.WHITE)
    black_material = sum(piece_values.get(p.piece_type, 0) for p in board.piece_map().values() if p.color == chess.BLACK)
    material_diff = white_material - black_material

    if material_diff > 3:
        context.append("White has a significant material advantage.")
    elif material_diff < -3:
        context.append("Black has a significant material advantage.")

    # Echec
    if board.is_check():
        context.append("The opponent is in check.")

    # Capture
    if board.is_capture(move):
        captured = board.piece_at(move.to_square)
        if captured:
            context.append(f"This move captures a {chess.piece_name(captured.piece_type)}.")

    # Fin de partie proche
    if board.is_game_over():
        context.append("The game is over.")
    elif board.legal_moves.count() < 5:
        context.append("The opponent has very few legal moves left.")

    # Phase de jeu
    total_pieces = len(board.piece_map())
    if total_pieces > 20:
        context.append("We are in the opening/middlegame.")
    else:
        context.append("We are in the endgame.")

    return " ".join(context)

def generate_commentary(board: chess.Board, move: chess.Move) -> str:
    move_san = board.san(move)
    piece = board.piece_at(move.from_square)
    piece_name = chess.piece_name(piece.piece_type) if piece else "piece"
    position_context = get_position_context(board, move)

    # Variation de style pour éviter la répétition
    styles = [
        "analytical and precise",
        "confident and slightly arrogant",
        "calm and philosophical",
        "sharp and tactical",
        "dry and sarcastic"
    ]
    style = random.choice(styles)

    recent = "\n".join(_recent_comments[-5:]) if _recent_comments else "None"

    prompt = f"""You are TANUKI, an elegant chess bot with a sharp mind and unique personality.
You just played {move_san} ({piece_name}).

Position context: {position_context}
FEN: {board.fen()}

Your recent comments (DO NOT repeat similar phrases):
{recent}

Write ONE comment (max 2 sentences) in a {style} tone.
- Focus on WHY this move is strategically or tactically relevant
- Reference the position context when interesting
- Speak in first person
- No markdown, no asterisks, plain English only"""

    response = client.chat(
        model="llama3.1:8b",
        messages=[{"role": "user", "content": prompt}]
    )

    commentary = response["message"]["content"]

    # Mémorise pour anti-répétition
    _recent_comments.append(commentary[:100])
    if len(_recent_comments) > 10:
        _recent_comments.pop(0)

    return commentary