import websocket
import threading
import time

WARUDO_URL = "ws://localhost:19190"
RECONNECT_DELAY = 5

_ws = None
_connected = False
_lock = threading.Lock()


def _on_open(ws):
    global _connected
    _connected = True
    print("Warudo connecté")


def _on_close(ws, code, msg):
    global _connected
    _connected = False
    print(f"Warudo déconnecté (code={code})")


def _on_error(ws, error):
    global _connected
    _connected = False
    print(f"Warudo erreur : {error}")


def _run_loop():
    global _ws
    while True:
        try:
            with _lock:
                _ws = websocket.WebSocketApp(
                    WARUDO_URL,
                    on_open=_on_open,
                    on_close=_on_close,
                    on_error=_on_error,
                )
            _ws.run_forever()
        except Exception as e:
            print(f"Warudo connexion échouée : {e}")
        time.sleep(RECONNECT_DELAY)


threading.Thread(target=_run_loop, daemon=True).start()


def trigger(animation):
    global _ws
    if _connected and _ws:
        try:
            _ws.send(animation)
        except Exception as e:
            print(f"Warudo send erreur : {e}")
    else:
        print(f"Warudo non connecté — reconnexion en cours, animation ignorée : {animation}")
