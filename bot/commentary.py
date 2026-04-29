import ollama
import chess

client = ollama.Client(host="http://192.168.129.47:11434")

def generate_commentary(board: chess.Board, move: chess.Move) -> str:
    move_san = board.san(move)
    piece = board.piece_at(move.from_square)
    piece_name = chess.piece_name(piece.piece_type) if piece else "pièce"
    
    prompt = f"""You are TANUKI, an elegant and slightly sarcastic chess bot with a unique personality.
You just played the move {move_san} ({piece_name}).
Current FEN position: {board.fen()}

Comment this move in 1-2 sentences maximum. Be concise, smart, sometimes sarcastic.
Speak in first person. No markdown, just natural English text."""

    response = client.chat(
        model="llama3.1:8b",
        messages=[{"role": "user", "content": prompt}]
    )
    
    return response["message"]["content"]