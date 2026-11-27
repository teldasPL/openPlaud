#!/usr/bin/env python3
"""
openPlaud — iteracja 0, test 1: połączenie z kontem PLAUD.

Co robi:
  1. Otwiera przeglądarkę z logowaniem PLAUD (logujesz się sam — skrypt nie widzi hasła).
  2. Odbiera kod autoryzacji na http://localhost:8199 i wymienia go na token (OAuth 2.0 + PKCE).
  3. Wypisuje 10 ostatnich nagrań z Twojego konta.
  4. Pobiera audio jednego nagrania do folderu downloads/ (bez transkrypcji — nie zużywa minut).

Tylko biblioteka standardowa Pythona 3 (działa na macOS bez instalacji pakietów).

Źródło wiedzy o API: projekt plaudit (MIT) — czysta reimplementacja oficjalnego Plaud CLI.
Uwaga: to API nie jest oficjalnie przeznaczone dla aplikacji firm trzecich (ryzyko R1).
"""
import base64
import hashlib
import http.server
import json
import os
import secrets
import shutil
import subprocess
import socketserver
import stat
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
import webbrowser

CLIENT_ID = "client_f9e0b214-c11f-434b-8b95-c4497d1feb81"  # publiczny klient Plaud CLI
REDIRECT_URI = "http://localhost:8199/auth/callback"
PORT = 8199
AUTH_URL = "https://web.plaud.ai/platform/oauth"
TOKEN_URL = "https://platform.plaud.ai/developer/api/oauth/third-party/access-token"
REFRESH_URL = "https://platform.plaud.ai/developer/api/oauth/third-party/access-token/refresh"
API = "https://platform.plaud.ai/developer/api"

HERE = os.path.dirname(os.path.abspath(__file__))
SECRETS_DIR = os.path.join(HERE, ".secrets")
TOKEN_FILE = os.path.join(SECRETS_DIR, "plaud_tokens.json")
DOWNLOADS = os.path.join(HERE, "downloads")
# Domyślny podpis "Python-urllib" bywa blokowany przez zaporę serwera (HTTP 403).
USER_AGENT = "openPlaud/0.1 (+https://github.com/teldasPL/openPlaud)"


def open_url(req, timeout=30):
    """urlopen z własnym User-Agent i czytelnym opisem błędu HTTP (bez tokenów)."""
    if isinstance(req, str):
        req = urllib.request.Request(req)
    req.add_header("User-Agent", USER_AGENT)
    try:
        return urllib.request.urlopen(req, timeout=timeout)
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "replace")[:500]
        host = urllib.parse.urlparse(req.full_url).netloc
        sys.exit(
            f"\nBŁĄD HTTP {e.code} z {host}{urllib.parse.urlparse(req.full_url).path}\n"
            f"Serwer: {e.headers.get('Server')}  CF-Ray: {e.headers.get('CF-Ray')}\n"
            f"Treść odpowiedzi: {body}\n\nWklej ten komunikat do czatu."
        )


def b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def save_tokens(tok: dict) -> None:
    os.makedirs(SECRETS_DIR, exist_ok=True)
    os.chmod(SECRETS_DIR, stat.S_IRWXU)
    with open(TOKEN_FILE, "w") as f:
        json.dump(tok, f, indent=2)
    os.chmod(TOKEN_FILE, stat.S_IRUSR | stat.S_IWUSR)


def load_tokens():
    try:
        with open(TOKEN_FILE) as f:
            return json.load(f)
    except FileNotFoundError:
        return None


def post_form(url: str, fields: dict, headers=None) -> dict:
    body = urllib.parse.urlencode(fields).encode()
    req = urllib.request.Request(url, data=body, method="POST")
    req.add_header("Accept", "application/json")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    for k, v in (headers or {}).items():
        req.add_header(k, v)
    with open_url(req) as r:
        return json.loads(r.read())


def to_tokenset(resp: dict, fallback_refresh=None) -> dict:
    exp = resp.get("expires_in")
    return {
        "access_token": resp["access_token"],
        "refresh_token": resp.get("refresh_token") or fallback_refresh,
        "expires_at": int(time.time() * 1000) + exp * 1000 if exp else None,
    }


def login() -> dict:
    verifier = b64url(secrets.token_bytes(32))
    challenge = b64url(hashlib.sha256(verifier.encode()).digest())
    state = b64url(secrets.token_bytes(16))
    result = {}

    class Handler(http.server.BaseHTTPRequestHandler):
        def log_message(self, *a):
            pass

        def do_GET(self):
            u = urllib.parse.urlparse(self.path)
            q = urllib.parse.parse_qs(u.query)
            msg = "Wróć do okna terminala."
            if u.path == "/auth/callback":
                if "error" in q:
                    result["error"] = q["error"][0]
                    msg = "Logowanie nieudane."
                elif q.get("state", [""])[0] == state and "code" in q:
                    result["code"] = q["code"][0]
                    msg = "Połączono z PLAUD. Możesz zamknąć tę kartę."
            page = f"<!doctype html><meta charset=utf-8><body style='font-family:system-ui;text-align:center;padding:3rem'><h2>openPlaud</h2><p>{msg}</p>"
            data = page.encode()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

    socketserver.TCPServer.allow_reuse_address = True
    srv = socketserver.TCPServer(("127.0.0.1", PORT), Handler)
    t = threading.Thread(target=srv.serve_forever, daemon=True)
    t.start()

    params = {
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
        "code_challenge": challenge,
        "code_challenge_method": "S256",
        "state": state,
    }
    url = AUTH_URL + "?" + urllib.parse.urlencode(params)
    print("\n>>> Otwieram przeglądarkę. Zaloguj się do PLAUD i zatwierdź dostęp.")
    print("    Jeśli przeglądarka się nie otworzy, wklej ten adres ręcznie:\n    " + url + "\n")
    webbrowser.open(url)

    deadline = time.time() + 300
    while time.time() < deadline and not result:
        time.sleep(0.5)
    srv.shutdown()

    if "error" in result:
        sys.exit(f"Odmowa autoryzacji: {result['error']}")
    if "code" not in result:
        sys.exit("Nie otrzymano kodu w ciągu 5 minut.")

    basic = base64.b64encode(f"{CLIENT_ID}:".encode()).decode()
    resp = post_form(
        TOKEN_URL,
        {"code": result["code"], "redirect_uri": REDIRECT_URI, "code_verifier": verifier, "state": state},
        {"Authorization": f"Basic {basic}"},
    )
    tok = to_tokenset(resp)
    save_tokens(tok)
    return tok


def access_token() -> str:
    tok = load_tokens()
    if tok and tok.get("expires_at") and time.time() * 1000 > tok["expires_at"] - 60_000:
        if tok.get("refresh_token"):
            try:
                tok = to_tokenset(post_form(REFRESH_URL, {"refresh_token": tok["refresh_token"]}), tok["refresh_token"])
                save_tokens(tok)
            except Exception:
                tok = None
        else:
            tok = None
    if not tok:
        tok = login()
    return tok["access_token"]


def api_get(path: str) -> dict:
    req = urllib.request.Request(API + path)
    req.add_header("Authorization", f"Bearer {access_token()}")
    req.add_header("Accept", "application/json")
    with open_url(req) as r:
        return json.loads(r.read())


def fmt_dur(ms):
    if not ms:
        return "?"
    s = int(ms) // 1000  # API zwraca milisekundy (potwierdzone w T1)
    return f"{s // 3600}:{s % 3600 // 60:02d}:{s % 60:02d}"


def main():
    me = api_get("/open/third-party/users/current")
    print("Zalogowano jako:", json.dumps(me, ensure_ascii=False)[:200])

    page = api_get("/open/third-party/files/?page=1&page_size=10")
    files = page.get("data", [])
    if not files:
        print("Brak nagrań na koncie.")
        return
    print("\nOstatnie nagrania:")
    for i, f in enumerate(files, 1):
        print(f"  {i:2d}. {f.get('start_at') or f.get('created_at') or '?':25s}  {fmt_dur(f.get('duration')):>9s}  {f.get('name') or f['id']}")

    choice = os.environ.get("PICK", "1")
    f = files[int(choice) - 1]
    detail = api_get(f"/open/third-party/files/{f['id']}")
    url = detail.get("presigned_url")
    raw = {k: v for k, v in detail.items() if k not in ("source_list", "note_list", "presigned_url")}
    print("\nSzczegóły nagrania:", json.dumps(raw, ensure_ascii=False))
    print("Ma transkrypcję PLAUD:", bool(detail.get("source_list")))
    if not url:
        print("Brak linku do audio dla tego nagrania.")
        return

    os.makedirs(DOWNLOADS, exist_ok=True)
    ext = os.path.splitext(urllib.parse.urlparse(url).path)[1] or ".audio"
    out = os.path.join(DOWNLOADS, f"{f['id']}{ext}")
    print(f"\nPobieram audio → {out}")
    t0 = time.time()
    with open_url(url, timeout=120) as r, open(out, "wb") as w:
        ctype = r.headers.get("Content-Type")
        while chunk := r.read(1 << 20):
            w.write(chunk)
    size = os.path.getsize(out)
    print(f"Gotowe: {size / 1e6:.1f} MB, typ: {ctype}, czas: {time.time() - t0:.1f} s")
    base = os.path.join(DOWNLOADS, f["id"])
    save_plaud_texts(detail, base)
    to_wav(out, base + ".wav")
    print("\nTEST 1: OK")


def save_plaud_texts(detail: dict, base: str) -> None:
    """Zapisuje istniejącą transkrypcję i podsumowanie PLAUD (do porównania w T2/T3)."""
    for item in detail.get("source_list") or []:
        if item.get("data_type") == "transaction":
            try:
                segs = json.loads(item.get("data_content") or "[]")
            except json.JSONDecodeError:
                continue
            lines = [f"[{fmt_dur(sg.get('start_time'))}] {sg.get('speaker') or ''}: {sg.get('content', '')}" for sg in segs]
            with open(base + "_plaud_transkrypcja.txt", "w") as fh:
                fh.write("\n".join(lines))
            print(f"Zapisano transkrypcję PLAUD → {base}_plaud_transkrypcja.txt ({len(segs)} fragmentów)")
    for item in detail.get("note_list") or []:
        if item.get("data_type") == "auto_sum_note" and item.get("data_content"):
            with open(base + "_plaud_podsumowanie.md", "w") as fh:
                fh.write(item["data_content"])
            print(f"Zapisano podsumowanie PLAUD → {base}_plaud_podsumowanie.md")


def to_wav(src: str, dst: str) -> None:
    """Ogg/Opus → WAV 16 kHz mono (iPhone nie czyta .ogg; potrzebne do T2)."""
    if not shutil.which("ffmpeg"):
        print("Brak ffmpeg — pomijam konwersję do WAV (instalacja: brew install ffmpeg).")
        return
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", src, "-ac", "1", "-ar", "16000", "-c:a", "pcm_s16le", dst], check=True)
    print(f"Przekonwertowano do WAV → {dst} ({os.path.getsize(dst) / 1e6:.0f} MB)")


if __name__ == "__main__":
    main()
