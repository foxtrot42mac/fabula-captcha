# fabula-captcha

**Phrase-based image CAPTCHA — no Google, no tracking, self-hosted.**

## Concept

Fabula CAPTCHA shows the user a simple image and asks them to describe it in words.
The server normalises the phrase (), hashes it (SHA-256), and
compares it against a set of pre-approved hashes for that image.



No ML classifier. No third-party requests. Multiple accepted phrases per image
give semantic flexibility while keeping the server logic trivial.

## Quick start



Requires Python 3.9+, stdlib only.

## Demo

https://foxtrot42.org/captcha

## API

| Method | Path | Description |
|--------|------|-------------|
| GET |  | HTML demo page |
| GET |  | Random challenge JSON |
| POST |  | Verify phrase |

**GET /captcha/challenge** — response:


**POST /captcha/verify** — request:

Response:


## Adding challenges

Edit . For each challenge provide:
- uid=1000(mac42) gid=1000(mac42) groups=1000(mac42),4(adm),24(cdrom),27(sudo),30(dip),46(plugdev),100(users) — unique string key
-  — inline SVG image
-  — question shown to user
-  — list of acceptable phrases (server pre-hashes them on startup)

## License

Non-commercial free. Commercial use requires written permission — hello@foxtrot42.org
See [LICENSE](LICENSE).
