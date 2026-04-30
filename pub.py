import obsws_python as obs
import time
import threading
import os
from dotenv import load_dotenv

load_dotenv()

def pub_loop():
    client = obs.ReqClient(host='localhost', port=4455, password=os.getenv("OBS_PASSWORD"))
    
    while True:
        # Bandeau visible pendant 55 minutes
        time.sleep(55 * 60)
        
        # Cache le bandeau pendant 5 minutes
        item_id = client.get_scene_item_id('TanukiChessBot', 'Bandeau').scene_item_id
        client.set_scene_item_enabled(
            scene_name='TanukiChessBot',
            item_id=item_id,
            enabled=False
        )
        
        time.sleep(5 * 60)
        
        # Réaffiche le bandeau
        client.set_scene_item_enabled(
            scene_name='TanukiChessBot',
            item_id=item_id,
            enabled=True
        )

threading.Thread(target=pub_loop, daemon=True).start()