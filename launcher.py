"""Входная точка для PyInstaller --onedir."""
from pathlib import Path
import os
import sys
import socket
import time
import threading
import webbrowser
from waitress import serve

# Изменяемая БД находится вне ресурсов .exe и сохраняется между запусками.
if sys.platform=='win32':
    base=Path(os.environ.get('LOCALAPPDATA',str(Path.home()))) / 'Mythoria'
else: base=Path.home()/'.characterlab'
base.mkdir(parents=True,exist_ok=True)
os.environ.setdefault('MYTHORIA_DB',str(base/'mythoria.sqlite3'))
from characterlab import create_app

def select_port():
    for port in range(5000,5030):
        with socket.socket() as s:
            try: s.bind(('127.0.0.1',port));return port
            except OSError: pass
    raise RuntimeError('Нет доступного локального порта')

if __name__=='__main__':
    port=select_port();app=create_app();url=f'http://127.0.0.1:{port}'
    def show():
        for _ in range(120):
            try:
                with socket.create_connection(('127.0.0.1',port),timeout=.15):
                    webbrowser.open(url);return
            except OSError: time.sleep(.1)
    threading.Thread(target=show,daemon=True).start()
    print('Mythoria:',url)
    serve(app,host='127.0.0.1',port=port,threads=4)
