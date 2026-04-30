import json
import os

STATS_FILE = os.path.join(os.path.dirname(__file__), '..', 'stats.json')
SCORE_FILE = os.path.join(os.path.dirname(__file__), '..', 'score.txt')

def load_stats():
    if os.path.exists(STATS_FILE):
        with open(STATS_FILE, 'r') as f:
            return json.load(f)
    return {"total": 0, "bot_wins": 0, "human_wins": 0, "draws": 0}

def save_stats(stats):
    with open(STATS_FILE, 'w') as f:
        json.dump(stats, f)

def write_score_file():
    stats = load_stats()
    score = f"P: {stats['total']}\nW: {stats['bot_wins']}\nL: {stats['human_wins']}\nD: {stats['draws']}"
    with open(SCORE_FILE, 'w', encoding='utf-8') as f:
        f.write(score)

def record_result(result, bot_color):
    stats = load_stats()
    stats["total"] += 1
    if result == "1-0":
        if bot_color == "white":
            stats["bot_wins"] += 1
        else:
            stats["human_wins"] += 1
    elif result == "0-1":
        if bot_color == "black":
            stats["bot_wins"] += 1
        else:
            stats["human_wins"] += 1
    else:
        stats["draws"] += 1
    save_stats(stats)
    write_score_file()
    return stats

def get_score_text():
    stats = load_stats()
    return (f"Parties jouées : {stats['total']} | "
            f"Tanuki : {stats['bot_wins']} | "
            f"Humains : {stats['human_wins']} | "
            f"Nuls : {stats['draws']}")