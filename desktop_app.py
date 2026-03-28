import threading
import time
import webview

from app import create_app
from app.updater import check_and_offer_update
from app.version import __version__, APP_NAME, GITHUB_REPO

app = create_app()


def _run_flask():
    app.run(host="127.0.0.1", port=5000, debug=False, use_reloader=False)


def main():
    check_and_offer_update(__version__, GITHUB_REPO, APP_NAME)

    t = threading.Thread(target=_run_flask, daemon=True)
    t.start()
    time.sleep(1)

    window = webview.create_window(
        APP_NAME,
        "http://127.0.0.1:5000",
        width=1100,
        height=750,
        resizable=True,
    )
    webview.start()


if __name__ == "__main__":
    main()
