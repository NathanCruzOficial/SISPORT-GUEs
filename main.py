import threading
import time
import webbrowser

from waitress import serve
from app import create_app
from app.updater import check_and_offer_update
from app.version import __version__, APP_NAME, GITHUB_REPO

print("App Iniciado com sucesso!")
serve(create_app(), host="127.0.0.1", port=5000)


HOST = "127.0.0.1"
PORT = 5000

def open_browser_when_ready(url: str, delay: float = 0.8):
    time.sleep(delay)
    webbrowser.open(url)

def main():
    check_and_offer_update(__version__, GITHUB_REPO, APP_NAME)

    url = f"http://{HOST}:{PORT}/"
    threading.Thread(target=open_browser_when_ready, args=(url,), daemon=True).start()

    app = create_app()
    app.run(host=HOST, port=PORT, debug=False, use_reloader=False)
    

if __name__ == "__main__":
    main()
