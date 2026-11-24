"""Общий локальный запуск браузерной версии (Windows/macOS)."""
import socket
import threading
import webbrowser
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from characterlab import create_app
from waitress import serve

def available_port(host='127.0.0.1',start=5000):
    for port in range(start,start+30):
        with socket.socket() as sock:
            try: sock.bind((host,port));return port
            except OSError: continue
    raise RuntimeError('Не найден свободный порт (5000–5029)')

if __name__=='__main__':
    port=available_port()
    app=create_app()
    url=f'http://127.0.0.1:{port}'
    print('Mythoria работает:',url)
    # Открываем браузер после готовности локального HTTP-сервера.
    def open_when_ready():
        import time
        for _ in range(100):
            try:
                with socket.create_connection(('127.0.0.1',port),timeout=.15):
                    webbrowser.open(url);return
            except OSError: time.sleep(.1)
    threading.Thread(target=open_when_ready,daemon=True).start()
    serve(app,host='127.0.0.1',port=port,threads=4)
