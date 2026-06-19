#!/usr/bin/env python3
"""
Fabula CAPTCHA — phrase-based image CAPTCHA server
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

# Precompute accepted hash sets
HASH_MAP = {}
for ch in CAPTCHA_DATA["challenges"]:
    HASH_MAP[ch["id"]] = {phrase_hash(p) for p in ch["accepted"]}

HTML_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Fabula CAPTCHA — Demo</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600&display=swap" rel="stylesheet">
<style>
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    font-family: 'Space Grotesk', sans-serif;
    background: #f8fafc;
    color: #0f172a;
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 24px;
  }
  .card {
    background: white;
    border: 1px solid #e2e8f0;
    border-radius: 16px;
    padding: 36px;
    max-width: 420px;
    width: 100%;
    box-shadow: 0 4px 24px rgba(0,0,0,0.06);
  }
  .logo {
    font-size: 13px;
    font-weight: 600;
    color: #2563eb;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin-bottom: 24px;
  }
  h1 { font-size: 22px; font-weight: 600; margin-bottom: 6px; }
  .sub { font-size: 14px; color: #64748b; margin-bottom: 28px; }
  .image-box {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    height: 220px;
    margin-bottom: 20px;
    overflow: hidden;
    position: relative;
  }
  .image-box svg { max-width: 200px; max-height: 200px; }
  .prompt { font-size: 14px; color: #475569; margin-bottom: 12px; font-weight: 500; }
  input[type=text] {
    width: 100%;
    padding: 12px 16px;
    border: 1.5px solid #e2e8f0;
    border-radius: 10px;
    font-family: inherit;
    font-size: 15px;
    color: #0f172a;
    outline: none;
    transition: border-color 0.15s;
    margin-bottom: 14px;
  }
  input[type=text]:focus { border-color: #2563eb; }
  .btn-row { display: flex; gap: 10px; }
  button {
    flex: 1;
    padding: 12px;
    border: none;
    border-radius: 10px;
    font-family: inherit;
    font-size: 15px;
    font-weight: 600;
    cursor: pointer;
    transition: background 0.15s, opacity 0.15s;
  }
  .btn-verify { background: #2563eb; color: white; }
  .btn-verify:hover { background: #1d4ed8; }
  .btn-new { background: #f1f5f9; color: #475569; }
  .btn-new:hover { background: #e2e8f0; }
  .result {
    margin-top: 16px;
    padding: 12px 16px;
    border-radius: 10px;
    font-size: 14px;
    font-weight: 500;
    display: none;
  }
  .result.ok { background: #dcfce7; color: #15803d; border: 1px solid #bbf7d0; }
  .result.fail { background: #fee2e2; color: #dc2626; border: 1px solid #fecaca; }
  .footer {
    margin-top: 28px;
    font-size: 12px;
    color: #94a3b8;
    text-align: center;
  }
  .footer a { color: #2563eb; text-decoration: none; }
</style>
</head>
<body>
<div class="card">
  <div class="logo">Fabula CAPTCHA</div>
  <h1>Prove you're human</h1>
  <p class="sub">Describe what you see in the image below</p>
  <div class="image-box" id="imgBox">
    <div style="color:#94a3b8;font-size:14px;">Loading...</div>
  </div>
  <p class="prompt" id="promptText"></p>
  <input type="text" id="phrase" placeholder="Type your answer..." autocomplete="off" />
  <div class="btn-row">
    <button class="btn-verify" onclick="verify()">Verify</button>
    <button class="btn-new" onclick="loadChallenge()">New image</button>
  </div>
  <div class="result" id="result"></div>
</div>
<div class="footer">
  <a href="https://github.com/foxtrot42mac/fabula-captcha">fabula-captcha</a> &mdash;
  self-hosted, no tracking, no ML
</div>
<script>
let currentId = null;

async function loadChallenge() {
  document.getElementById('result').style.display = 'none';
  document.getElementById('phrase').value = '';
  document.getElementById('imgBox').innerHTML = '<div style="color:#94a3b8;font-size:14px;">Loading...</div>';
  const r = await fetch('/captcha/challenge');
  const data = await r.json();
  currentId = data.id;
  document.getElementById('imgBox').innerHTML = data.image_svg;
  document.getElementById('promptText').textContent = data.prompt;
}

async function verify() {
  const phrase = document.getElementById('phrase').value.trim();
  if (!phrase || !currentId) return;
  const r = await fetch('/captcha/verify', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({id: currentId, phrase})
  });
  const data = await r.json();
  const el = document.getElementById('result');
  el.style.display = 'block';
  if (data.ok) {
    el.className = 'result ok';
    el.textContent = '✓ Verified! You passed the CAPTCHA.';
  } else {
    el.className = 'result fail';
    el.textContent = '✗ Not quite — try a different description.';
  }
}

document.getElementById('phrase').addEventListener('keydown', e => {
  if (e.key === 'Enter') verify();
});

loadChallenge();
</script>
</body>
</html>
"""

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
            self.send_json(200, {
                "id": ch["id"],
                "image_svg": ch["svg"],
                "prompt": ch["prompt"]
            })

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
            phrase = body.get("phrase", "")

            if cid not in HASH_MAP:
                self.send_json(400, {"error": "unknown challenge id"})
                return

            h = phrase_hash(phrase)
            ok = h in HASH_MAP[cid]
            self.send_json(200, {"ok": ok})
        else:
            self.send_json(404, {"error": "not found"})


if __name__ == "__main__":
    port = 8019
    server = HTTPServer(("127.0.0.1", port), CaptchaHandler)
    print(f"Fabula CAPTCHA listening on port {port}")
    server.serve_forever()
