# Fabula CAPTCHA — Protocol Specification

**Version:** 1.1
**Date:** 2026-06-19
**Author:** foxtrot42

---

## Concept

Fabula CAPTCHA is a phrase-based image CAPTCHA that requires no machine learning,
no third-party services, and leaves no tracking cookies. The server presents an
image; the user either types a short phrase or selects from a list of buttons;
the server checks the answer against a pre-approved set stored as SHA-256 hashes.

### Why phrase-based?

- Trivial for humans, hard to automate without a vision LLM
- Multiple accepted phrases per image provide semantic flexibility
- No pixel-level ML classifier needed on the server side
- Server-side logic is ~60 lines of Python

---

## Architecture

Client receives: image SVG, prompt, shuffled button list, select mode.
Client never receives: valid_hashes, plaintext accepted phrases.

---

## Endpoints

### GET /captcha/challenge

Returns a random challenge. Buttons are shuffled server-side on every request.
 is **never** included in the response.

**Response 200 (button-mix mode):**



 values:  (any single valid answer),  (all valid answers),
or an integer N (at least N valid answers).

### POST /captcha/verify

Verify a user's answer(s) against a challenge.

**Request body (JSON):**



 is always an array. Legacy single-string  field is also accepted.

**Response 200:**



or



---

## Phrase Normalisation



The server stores only SHA-256 hashes of accepted phrases — not the phrases
themselves. This prevents trivial enumeration from a leaked data file.

---

## Challenge Data Format



At server startup,  are loaded into memory as a set per challenge.
The  list is the full mix of valid + distractor phrases.
The client sees the shuffled buttons but **never** learns which are valid.

---

## Security model: the asymmetry

Fabula CAPTCHA relies on three compounding asymmetries rather than one hard problem.

### 1. Knowledge asymmetry

 (and the plaintext phrases behind them) are known only to the site
owner. The phrase vocabulary is never published. An attacker who intercepts the
challenge response sees only shuffled buttons — they cannot distinguish valid
answers from distractors without already knowing the vocabulary or solving the image.

### 2. Economic asymmetry — LLM attack

A vision LLM (GPT-4o, Claude Opus, etc.) can describe the image correctly with high
probability. But each API call costs several cents, and a successful attack requires
the model's output to match a phrase in the closed vocabulary — a vocabulary the
attacker cannot see. With rate-limiting and IP banning, the cost-per-success ratio
rises steeply. A cheap CAPTCHA becomes an expensive attack surface.

### 3. Economic asymmetry — human farm attack

Human solving farms are cheaper per solve than LLMs. However:

- The closed vocabulary is invisible to the farm (unlike reCAPTCHA, where all
  challenge images and labels are public knowledge).
- A farm worker must guess which button label is "correct" — they see the same
  shuffled mix as a bot. Without prior knowledge, per-solve accuracy drops.
- Rate limiting + IP banning makes volume attacks expensive to sustain.

This is not a silver bullet. But it shifts the economics meaningfully compared to
a CAPTCHA with a publicly known answer space.

---

## What this does NOT replace

- **FIDO2 / WebAuthn** — hardware-backed authentication is categorically stronger.
  Use FIDO2 for account security; use Fabula CAPTCHA for anonymous form spam.
- **Targeted attacks with vocabulary knowledge** — if an attacker already knows
  your phrase set (insider threat, leaked config), the knowledge asymmetry collapses.
- **High-security financial operations** — for anything involving money or
  sensitive PII, add a second factor; do not rely on a CAPTCHA alone.

---

## Extensions (concept, not implemented)

**Auto-labelling via vision LLM**

A dataset can be labelled automatically: feed each SVG image to a vision LLM,
ask it to generate plausible descriptions (valid) and semantically nearby
non-descriptions (distractors). The same model that could *attack* the CAPTCHA
on a public site can *build* the dataset privately. On the production site,
the vocabulary is closed — the model that built it cannot trivially pass it.

**Input modes**

Two interaction modes, selectable per challenge:

-  — user types a free-form description. The server reveals nothing about
  the answer space. Most secure; slightly higher UX friction on mobile.
-  — server returns a shuffled list of 5 options (valid + distractors)
  and a  parameter. The client renders clickable choices. More mobile-
  friendly; leaks the button labels (though not which are valid).

---

## Integration Example

See  for a minimal JS widget (~30 lines, no deps).

---

## Security Analysis

### What it protects against

- **Simple bots** — form submission bots without vision capability fail
- **Tracking** — no third-party requests; CAPTCHA runs 100% server-side
- **Enumeration** — hashed accepted set leaks no plaintext phrases

### What it does NOT protect against

- **LLM-powered bots** — a GPT-4o or similar vision model can likely describe
  images correctly. For high-security use cases, add: session tokens, rate
  limiting, image noise/distortion, rotating challenge sets.
- **Dictionary attacks on hashes** — with a small accepted set per image, an
  attacker who knows the vocabulary could try all options. Mitigate with rate
  limiting (e.g. 5 attempts / 10 minutes per IP).
- **Replay** — this demo has no session token; production use should issue a
  one-time challenge token and expire it after one verify call.

### Recommended hardening for production

1. Issue a signed, time-limited token per challenge (JWT or HMAC)
2. Rate-limit  per IP
3. Add mild SVG noise / random element variation per render
4. Rotate the accepted phrase set and  periodically
5. Log failed attempts for anomaly detection

---

## License

Non-commercial use is free. Commercial use requires written permission.
Contact: hello@foxtrot42.org
