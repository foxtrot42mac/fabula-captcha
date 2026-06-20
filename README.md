# fabula-captcha

**Image CAPTCHA based on visual similarity — no Google, no ML, self-hosted.**

## Concept

The user sees a simple image (e.g. a blue door) and five labeled buttons.
The prompt: **"Select all that look same."**

Some buttons share at least one visual parameter with the image (color or object type) — these pass.
Some share nothing — these are traps.

**There is no single correct answer.** Any description that matches the image on at least one
parameter (color, shape, object type) is accepted. This is the key mechanism:

- A **human** sees the image and intuitively selects what looks related.
- A **bot** sees only text labels with no image context — random selection hits the traps.

The demo is intentionally simple — two challenges, pure SVG, stdlib Python.
It demonstrates the principle, not a production image dataset.

## Live demo

**[https://foxtrot42.org/captcha](https://foxtrot42.org/captcha)**

## How it works

Each challenge has two distractor pools:

- **near** — descriptions that share one parameter with the image (valid answers)
- **far** — descriptions that share no parameter (traps)

On every request the server picks **1 correct + 2 near + 2 far** at random and shuffles.
The mix changes each load; the rule stays the same.

Verification: the server checks submitted phrases against SHA-256 hashes of valid descriptions.
The plaintext vocabulary and the near/far split are **never sent to the client.**

## Quick start



Requires Python 3.9+, stdlib only.

## API

| Method | Path | Description |
|--------|------|-------------|
| GET |  | HTML demo page |
| GET |  | Random challenge JSON |
| POST |  | Verify selection |

**GET /captcha/challenge** response:


 is **never** included in the response.

**POST /captcha/verify**:

Response:  or 

## Security model

**1. No exact answer** — the valid set is open (anything blue or anything door-shaped).
An attacker cannot learn the rule from the button labels alone.

**2. Traps are invisible** — 2 out of 5 buttons are always traps.
Random selection fails ~40% per attempt. Repeated attempts trigger rate limiting.

**3. LLM solving is expensive** — a vision model can describe the image, but matching a
private closed vocabulary costs API calls per attempt. Unlike reCAPTCHA, the vocabulary
is private and changes per deployment.

See [docs/FABULA_CAPTCHA.md](docs/FABULA_CAPTCHA.md) for full analysis.

## Adding challenges

Edit :



Hash a phrase: eea8383376247d02a3a32b9bad077bbf536d61ba1f3f54cf835074f28985992e  -

The dataset can be labeled automatically using a vision LLM over your image set.
See [docs/FABULA_CAPTCHA.md](docs/FABULA_CAPTCHA.md).

## License

Non-commercial use is free. Commercial use requires written permission — hello@foxtrot42.org  
See [LICENSE](LICENSE).
