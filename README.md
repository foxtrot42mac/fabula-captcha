# fabula-captcha

**Phrase-based image CAPTCHA — no Google, no tracking, self-hosted.**

## What it does

Fabula CAPTCHA shows the user a simple SVG image and asks them to describe it in words.
The server normalises the phrase (), hashes it with SHA-256, and
compares the hash against a pre-approved set for that challenge.

No ML classifier. No third-party requests. Multiple accepted phrases per image
give semantic flexibility while keeping the server logic trivial (~60 lines of Python).

## Input modes

Input mode is a per-challenge setting configured in :

- **** (default) — user types a free-form description. The server exposes
  nothing about the answer space; only SHA-256 hashes are kept in memory. Most
  secure mode; slightly higher UX friction on mobile.

- **** — the challenge includes a  list (5 mixed options: valid
  answers + distractors) and a  parameter. The client renders clickable
  choices; the server verifies the chosen phrase(s) exactly like free-text mode.
  The  parameter controls how many valid answers are required:
  -  — any single valid choice passes
  -  — all valid choices must be selected
  -  (integer) — at least N valid choices must be selected

  The server shuffles  on every  request.
   is **never** sent to the client.

## Quick start



Requires Python 3.9+, stdlib only.

## Live demo

https://foxtrot42.org/captcha

## API

| Method | Path | Description |
|--------|------|-------------|
| GET |  | HTML demo page |
| GET |  | Random challenge JSON |
| POST |  | Verify phrase(s) |

**GET /captcha/challenge** — response:



 and  are included only for button-mode challenges.

**POST /captcha/verify** — request body:



 is an array. Legacy  (string) is also accepted.

Response:



## Security model

Three asymmetries protect the closed vocabulary:

1. **Knowledge asymmetry** —  (and the plaintext vocabulary) are
   known only to the site owner. An attacker who intercepts the challenge sees
   shuffled buttons but cannot distinguish valid from distractor without prior
   knowledge.

2. **Economic asymmetry (LLM)** — a vision LLM can likely describe the image
   correctly, but matching the closed vocabulary costs cents per attempt and
   requires rate-limit evasion. A cheap defense becomes an expensive attack.

3. **Economic asymmetry (human farm)** — farms cannot see the vocabulary (unlike
   reCAPTCHA where labels are public), so per-solve accuracy drops without prior
   knowledge. Rate limiting + IP banning makes volume attacks impractical.

See [](docs/FABULA_CAPTCHA.md) for full security analysis,
what this does not replace (FIDO2, high-security auth), and extension concepts.

## Adding challenges

Edit . For each challenge provide:

- uid=1000(mac42) gid=1000(mac42) groups=1000(mac42),4(adm),24(cdrom),27(sudo),30(dip),46(plugdev),100(users) — unique string key
-  — inline SVG image
-  — question shown to user
-  — list of 5 phrases (valid + distractors mixed)
-  — SHA-256 hashes of the valid phrases (normalized: strip + lower)
-  — , , or integer N

Hash a phrase:
60d12b7e998bebfe1086a95bdf987fe496d94ffd6517c000d3bd580f18e2486a

The plaintext vocabulary never leaves the server. Only SHA-256 hashes are kept
in memory at runtime.

## Integration

See [](examples/integration.html) for a minimal
drop-in widget (~30 lines of JS, no dependencies).

## License

Non-commercial use is free. Commercial use requires written permission — hello@foxtrot42.org
See [LICENSE](LICENSE).
