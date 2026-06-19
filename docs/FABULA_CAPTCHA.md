# Fabula CAPTCHA — Protocol Specification

**Version:** 1.0  
**Date:** 2026-06-19  
**Author:** foxtrot42

---

## Concept

Fabula CAPTCHA is a phrase-based image CAPTCHA that requires no machine learning,
no third-party services, and leaves no tracking cookies. The server presents an
image; the user types a short phrase describing it; the server checks the phrase
against a pre-approved set.

### Why phrase-based?

- Trivial for humans, hard to automate without a vision LLM
- Multiple accepted phrases per image provide semantic flexibility
- No pixel-level ML classifier needed on the server side
- Server-side logic is ~20 lines of Python

---

## Architecture



---

## Endpoints

### GET /captcha/challenge

Returns a random challenge.

**Response 200:**


### POST /captcha/verify

Verify a user's phrase against a challenge.

**Request body (JSON):**


**Response 200:**

or


---

## Phrase Normalisation



The server stores only SHA-256 hashes of accepted phrases — not the phrases
themselves. This prevents trivial enumeration from a leaked data file.

---

## Challenge Data Format

:



At server startup,  phrases are hashed and stored in a set. The plain
text list should be kept private.

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
- **Dictionary attacks on hashes** — with ~10 accepted phrases per image, an
  attacker who knows the image ID could try common descriptions. Mitigate with
  rate limiting (e.g. 5 attempts / 10 minutes per IP).
- **Replay** — this demo has no session token; production use should issue a
  one-time challenge token and expire it after one verify call.

### Recommended hardening for production

1. Issue a signed, time-limited  per challenge (JWT or HMAC)
2. Rate-limit  per IP
3. Add mild SVG noise / random element variation
4. Rotate the accepted phrase set periodically
5. Log failed attempts for anomaly detection

---

## Integration Example



---

## License

Non-commercial use is free. Commercial use requires written permission.  
Contact: hello@foxtrot42.org
