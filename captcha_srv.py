#!/usr/bin/env python3
"""
Fabula CAPTCHA - phrase-based image CAPTCHA server
Port 8019
"""

import json
import hashlib
import random
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse

DATA_FILE = os.path.join(os.path.dirname(__file__), "captcha_data.json")

with open(DATA_FILE) as f:
    CAPTCHA_DATA = json.load(f)

CHALLENGE_MAP = {c["id"]: c for c in CAPTCHA_DATA["challenges"]}

def normalize(phrase: str) -> str:
    return phrase.strip().lower()

def phrase_hash(phrase: str) -> str:
    return hashlib.sha256(normalize(phrase).encode()).hexdigest()

# Precompute valid hash sets from valid_hashes field
HASH_MAP = {}
for ch in CAPTCHA_DATA["challenges"]:
    HASH_MAP[ch["id"]] = set(ch["valid_hashes"])

HTML_PAGE = '<!DOCTYPE html>\n<html lang="en">\n<head>\n<meta charset="UTF-8">\n<meta name="viewport" content="width=device-width, initial-scale=1.0">\n<title>Fabula CAPTCHA — Demo</title>\n<link rel="preconnect" href="https://fonts.googleapis.com">\n<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600&display=swap" rel="stylesheet">\n<style>\n  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }\n  body { font-family: \'Space Grotesk\', sans-serif; background: #f8fafc; color: #0f172a; min-height: 100vh; display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 24px; }\n  .card { background: white; border: 1px solid #e2e8f0; border-radius: 16px; padding: 36px; max-width: 420px; width: 100%; box-shadow: 0 4px 24px rgba(0,0,0,0.06); }\n  .logo { font-size: 13px; font-weight: 600; color: #2563eb; letter-spacing: 0.08em; text-transform: uppercase; margin-bottom: 24px; }\n  h1 { font-size: 22px; font-weight: 600; margin-bottom: 6px; }\n  .sub { font-size: 14px; color: #64748b; margin-bottom: 28px; }\n  .image-box { background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 12px; display: flex; align-items: center; justify-content: center; height: 220px; margin-bottom: 20px; overflow: hidden; }\n  .image-box svg { max-width: 200px; max-height: 200px; }\n  .prompt { font-size: 14px; color: #475569; margin-bottom: 12px; font-weight: 500; }\n  .btn-choices { display: flex; flex-direction: column; gap: 8px; margin-bottom: 14px; }\n  .btn-choice { width: 100%; padding: 11px 16px; border: 1.5px solid #e2e8f0; border-radius: 10px; background: white; font-family: inherit; font-size: 14px; font-weight: 500; color: #0f172a; cursor: pointer; text-align: left; transition: border-color 0.15s, background 0.15s; }\n  .btn-choice:hover { border-color: #2563eb; background: #eff6ff; }\n  .btn-choice.selected { border-color: #2563eb; background: #dbeafe; color: #1d4ed8; }\n  input[type=text] { width: 100%; padding: 12px 16px; border: 1.5px solid #e2e8f0; border-radius: 10px; font-family: inherit; font-size: 15px; color: #0f172a; outline: none; transition: border-color 0.15s; margin-bottom: 14px; }\n  input[type=text]:focus { border-color: #2563eb; }\n  .btn-row { display: flex; gap: 10px; }\n  button { flex: 1; padding: 12px; border: none; border-radius: 10px; font-family: inherit; font-size: 15px; font-weight: 600; cursor: pointer; transition: background 0.15s, opacity 0.15s; }\n  .btn-verify { background: #2563eb; color: white; }\n  .btn-verify:hover { background: #1d4ed8; }\n  .btn-new { background: #f1f5f9; color: #475569; }\n  .btn-new:hover { background: #e2e8f0; }\n  .result { margin-top: 16px; padding: 12px 16px; border-radius: 10px; font-size: 14px; font-weight: 500; display: none; }\n  .result.ok { background: #dcfce7; color: #15803d; border: 1px solid #bbf7d0; }\n  .result.fail { background: #fee2e2; color: #dc2626; border: 1px solid #fecaca; }\n  .footer { margin-top: 28px; font-size: 12px; color: #94a3b8; text-align: center; }\n  .footer a { color: #2563eb; text-decoration: none; }\n</style>\n</head>\n<body>\n<div class="card">\n  <div class="logo">Fabula CAPTCHA</div>\n  <h1>Prove you\'re human</h1>\n  <p class="sub" id="subText">Describe what you see in the image below</p>\n  <div class="image-box" id="imgBox"><div style="color:#94a3b8;font-size:14px;">Loading...</div></div>\n  <p class="prompt" id="promptText"></p>\n  <div id="inputArea"></div>\n  <div class="btn-row">\n    <button class="btn-verify" onclick="verify()">Verify</button>\n    <button class="btn-new" onclick="loadChallenge()">New image</button>\n  </div>\n  <div class="result" id="result"></div>\n</div>\n<div class="footer">\n  <a href="https://github.com/foxtrot42mac/fabula-captcha">fabula-captcha</a> &mdash; self-hosted, no tracking, no ML\n</div>\n<script>\nlet currentId = null, currentButtons = null, currentSelect = null, selectedPhrases = [];\n\nfunction renderInput(data) {\n  const area = document.getElementById(\'inputArea\');\n  if (data.buttons && data.buttons.length) {\n    currentButtons = data.buttons; currentSelect = data.select; selectedPhrases = [];\n    const lbl = currentSelect === \'all\' ? \'Select all that apply\'\n      : (typeof currentSelect === \'number\' ? \'Select \' + currentSelect : \'Select one\');\n    document.getElementById(\'subText\').textContent = lbl;\n    var html = \'<div class="btn-choices">\';\n    data.buttons.forEach(function(btn, i) {\n      html += \'<button class="btn-choice" data-idx="\' + i + \'" onclick="toggleChoice(this)">\' + btn + \'</button>\';\n    });\n    html += \'</div>\';\n    area.innerHTML = html;\n  } else {\n    currentButtons = null;\n    document.getElementById(\'subText\').textContent = \'Describe what you see in the image below\';\n    area.innerHTML = \'<input type="text" id="phrase" placeholder="Type your answer..." autocomplete="off" />\';\n    document.getElementById(\'phrase\').addEventListener(\'keydown\', function(e) { if (e.key === \'Enter\') verify(); });\n  }\n}\n\nfunction toggleChoice(el) {\n  var phrase = currentButtons[parseInt(el.dataset.idx)];\n  var single = currentSelect === \'one\' || currentSelect === 1;\n  if (single) { document.querySelectorAll(\'.btn-choice\').forEach(function(b) { b.classList.remove(\'selected\'); }); selectedPhrases = []; }\n  if (el.classList.contains(\'selected\')) { el.classList.remove(\'selected\'); selectedPhrases = selectedPhrases.filter(function(p) { return p !== phrase; }); }\n  else { el.classList.add(\'selected\'); selectedPhrases.push(phrase); }\n}\n\nasync function loadChallenge() {\n  document.getElementById(\'result\').style.display = \'none\';\n  document.getElementById(\'imgBox\').innerHTML = \'<div style="color:#94a3b8;font-size:14px;">Loading...</div>\';\n  var r = await fetch(\'/captcha/challenge\');\n  var data = await r.json();\n  currentId = data.id;\n  document.getElementById(\'imgBox\').innerHTML = data.image_svg;\n  document.getElementById(\'promptText\').textContent = data.prompt;\n  renderInput(data);\n}\n\nasync function verify() {\n  var phrases = [];\n  if (currentButtons) {\n    phrases = selectedPhrases;\n    if (!phrases.length) return;\n  } else {\n    var v = document.getElementById(\'phrase\').value.trim();\n    if (!v || !currentId) return;\n    phrases = [v];\n  }\n  var r = await fetch(\'/captcha/verify\', {\n    method: \'POST\',\n    headers: {\'Content-Type\': \'application/json\'},\n    body: JSON.stringify({id: currentId, phrases: phrases})\n  });\n  var data = await r.json();\n  var el = document.getElementById(\'result\');\n  el.style.display = \'block\';\n  if (data.ok) { el.className = \'result ok\'; el.textContent = \'✓ Verified! You passed the CAPTCHA.\'; }\n  else { el.className = \'result fail\'; el.textContent = \'✗ Not quite — try a different answer.\'; }\n}\n\nloadChallenge();\n</script>\n</body>\n</html>'


class CaptchaHandler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass  # silent

    def send_json(self, code: int, obj: dict):
        body = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", len(body))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def send_html(self, html: str):
        body = html.encode()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", len(body))
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        path = urlparse(self.path).path.rstrip("/")

        if path in ("/captcha", ""):
            self.send_html(HTML_PAGE)

        elif path == "/captcha/challenge":
            ch = random.choice(CAPTCHA_DATA["challenges"])
            resp = {
                "id": ch["id"],
                "image_svg": ch["svg"],
                "prompt": ch["prompt"],
            }
            # Button-mix: shuffle, expose select; never expose valid_hashes
            if "buttons" in ch:
                buttons = list(ch["buttons"])
                random.shuffle(buttons)
                resp["buttons"] = buttons
                resp["select"] = ch.get("select", "one")
            self.send_json(200, resp)

        else:
            self.send_json(404, {"error": "not found"})

    def do_POST(self):
        path = urlparse(self.path).path.rstrip("/")

        if path == "/captcha/verify":
            length = int(self.headers.get("Content-Length", 0))
            try:
                body = json.loads(self.rfile.read(length))
            except Exception:
                self.send_json(400, {"error": "invalid json"})
                return

            cid = body.get("id", "")
            # Accept "phrases" array; legacy "phrase" string also supported
            phrases = body.get("phrases")
            if phrases is None:
                legacy = body.get("phrase", "")
                phrases = [legacy] if legacy else []

            if not isinstance(phrases, list):
                self.send_json(400, {"error": "phrases must be an array"})
                return

            if cid not in HASH_MAP:
                self.send_json(400, {"error": "unknown challenge id"})
                return

            valid_set = HASH_MAP[cid]
            ch = CHALLENGE_MAP[cid]
            select = ch.get("select", "one")

            if select == "all":
                submitted_hashes = {phrase_hash(p) for p in phrases}
                ok = submitted_hashes == valid_set
            elif select == "one":
                ok = any(phrase_hash(p) in valid_set for p in phrases)
            elif isinstance(select, int):
                valid_submitted = [p for p in phrases if phrase_hash(p) in valid_set]
                ok = len(set(valid_submitted)) >= select
            else:
                ok = any(phrase_hash(p) in valid_set for p in phrases)

            self.send_json(200, {"ok": ok})
        else:
            self.send_json(404, {"error": "not found"})


if __name__ == "__main__":
    port = 8019
    server = HTTPServer(("127.0.0.1", port), CaptchaHandler)
    print(f"Fabula CAPTCHA listening on port {port}")
    server.serve_forever()
