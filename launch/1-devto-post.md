---
title: "Your AI agent is getting 403'd. Here is the ID card the web now asks for."
published: false
description: "Web Bot Auth lets a bot prove who it is with a signature instead of a User-Agent string. Here is how the protocol works, and how to find out why your signed request still got blocked."
tags: ai, python, security, webdev
cover_image:
canonical_url:
---

You wrote an agent. It fetches a page. It worked on your laptop.

Then you shipped it, and now you get this:

```
HTTP 403 Forbidden
```

No reason. No header explaining what was wrong. Just a closed door.

This post is about why that happens in 2026, the standard that fixes it, and — the part
nobody talks about — how to find out which piece of your setup is broken when the
signature *still* does not work.

## Why the door closed

For thirty years, a bot said who it was by putting its name in a text header:

```
User-Agent: Googlebot/2.1 (+http://www.google.com/bot.html)
```

Anyone can type that. I can type that. That header is a claim, not proof, and once every
AI startup on earth started crawling, sites stopped believing claims. Cloudflare, Akamai,
Fastly and AWS WAF now block unrecognized automated traffic by default.

The fix the industry settled on is the same one we use everywhere else when a name is not
enough: **sign the request**.

That standard is **Web Bot Auth** — a specific way of using
[RFC 9421 HTTP Message Signatures](https://www.rfc-editor.org/info/rfc9421/). Cloudflare,
Amazon, Akamai and OpenAI are behind it, an IETF working group was chartered for it this
year, and Cloudflare's June 2026 Bot Management update made it a first-class signal. It is
not a proposal anymore. It is the turnstile.

## What Web Bot Auth actually is

It is smaller than it sounds. Three headers and one file.

**One:** you generate an Ed25519 keypair. The private key stays with your agent. The
public key goes in a JSON file you host at a fixed path on your own domain:

```
https://your-bot.example/.well-known/http-message-signatures-directory
```

That file is a JWKS — a JSON Web Key Set, which is just "a list of public keys in JSON".
Here is a real one, mine:

```json
{
  "keys": [
    {
      "kty": "OKP",
      "crv": "Ed25519",
      "x": "IfZCETKW4wWI1yeAygDHlsZ_qBNwKLPA6B5lWPXyC_0",
      "kid": "jrNMebzan34kcKhxGKB_uA8L8XzqMh9SA3dEh1i2gRY",
      "use": "sig",
      "alg": "EdDSA"
    }
  ]
}
```

**Two:** every outbound request carries three extra headers.

- `Signature-Agent` — the domain hosting that key file. This is you saying "my ID is
  issued over there."
- `Signature-Input` — which parts of the request you signed, plus when the signature was
  created, when it expires, which key you used (`keyid`), and the label
  `tag="web-bot-auth"`.
- `Signature` — the actual Ed25519 signature.

**Three:** the site fetches your key file, finds the key whose fingerprint matches
`keyid`, and checks the math. If it verifies, it knows the request came from whoever
controls that domain's private key. Not from someone who typed your name into a header.

The `keyid` is an [RFC 7638](https://www.rfc-editor.org/rfc/rfc7638) thumbprint — a hash
of the key itself, so the key names itself and cannot be mislabeled.

That is the whole protocol. A keypair, a hosted file, three headers.

## Seeing it work in 30 seconds

Talking about signatures is less useful than watching one flip a 403 into a 200. This runs
entirely on your machine, offline, with nothing to configure:

```bash
uvx wingfoot demo
```

```console
Reference verifier listening on http://127.0.0.1:59949

1. Unsigned request
   HTTP 403 Forbidden  unsigned or malformed: missing Signature-Input or Signature header

2. Signed request
   HTTP 200 OK  verified (keyid GY7VHzpJqnXO...)

Signing changed HTTP 403 to 200.
```

It starts a reference verifier in the same process, sends one request without a signature
and one with, and shows you both answers. That is the entire idea, demonstrated, before
you have created a key or hosted anything.

## The part that will actually cost you a weekend

Signing correctly is not the hard part. The cryptography is one library call.

The hard part is that **when it does not work, nothing tells you why.**

A verifier that rejects your signature returns `403`. That is all it returns. It will not
tell you that your clock is 40 seconds fast, or that your signature expired, or that your
key file returned HTML instead of JSON because your host redirected `/.well-known/` to a
404 page, or that you signed the right things but forgot `tag="web-bot-auth"`, or that
your directory is reachable but does not list the key you are actually signing with.

Every one of those is the same `403`. You are debugging a cryptographic handshake through
a one-bit channel.

That is the problem I built [**wingfoot**](https://github.com/AmirF194/wingfoot) around.
It signs requests, yes — but the command I actually use every day is `doctor`, which
checks each link in the chain separately and tells you which one is broken:

```console
$ wingfoot doctor https://fastinfer.org/

  ok   Bot identity
         keyid jrNMebzan34kcKhx...  directory at https://fastinfer.org
  ok   Signature is well-formed and cryptographically valid
         signing is correct per RFC 9421
  ok   Key directory reachable and publishes this key
         https://fastinfer.org/.well-known/http-message-signatures-directory
  ok   Directory response is signed
         verifiers can trust it

Probing the target
  -    Unsigned request
         HTTP 200
  ok   Signed request
         HTTP 200

The target accepted the request. (It also served the unsigned request, so it may not
require auth.)
```

Look at that last line, because it is the point of the tool. A `200` on a signed request
proves nothing on its own if the site would have served you anyway. A checker that
declared victory there would be lying to you. The useful signal is the *difference*
between the unsigned and signed responses, and each check tells you something a bare
status code cannot.

When a check fails, it says what failed and what to do about it — expired signature, clock
skew, unreachable directory, key not listed, missing tag.

## Putting it in your agent

Once your identity exists, signing is one argument on the HTTP client you already use.
Create the identity once:

```bash
wingfoot init --agent https://your-bot.example
wingfoot directory   # prints the JSON to host at the well-known path
```

Then:

```python
import requests, wingfoot
requests.get("https://example.com/", auth=wingfoot.requests_auth())
```

```python
import httpx, wingfoot
httpx.get("https://example.com/", auth=wingfoot.httpx_auth())
```

Each call is signed fresh, so a signature never goes stale in a long-running session.
Using some other client? `wingfoot.signed_headers(url)` hands you the three headers as a
plain dict and gets out of your way.

The library needs only `cryptography`. `requests` and `httpx` are optional extras.

## The step everyone forgets: verifiers need to know you exist

Here is the thing that surprises people, and I want to be straight about it because it is
the least fun part of this whole standard.

**A perfect signature does not get you through Cloudflare by itself.** The verifier has to
already know your key and have decided to trust it. That means registering — and no
provider offers automated registration yet. Each one runs a web form with a human review
behind it.

So `wingfoot register` does the only useful thing available: it checks your setup the way
a reviewer will, then prints every answer their forms ask for, ready to paste.

```console
$ wingfoot register --email you@example.com

Preflight — what a reviewer will check
  ok   Key directory reachable
  ok   Directory publishes this key
  ok   Directory response is signed

Cloudflare — Verified Bots
  form   https://dash.cloudflare.com/?to=/:account/configurations
    Bot / agent name          your-bot.example
    User-Agent                wingfoot/0.1.2 (+https://github.com/AmirF194/wingfoot)
    Key directory URL         https://your-bot.example/.well-known/...
```

Getting rejected because your directory was down when a reviewer looked at it is a bad way
to lose a week.

## Where this stands

Being honest about maturity: wingfoot is **alpha, v0.1.2**. Signing, verification, the
directory, and `doctor` all work and are tested against a reference verifier. What
`doctor` proves is that *your* side is correct — end-to-end acceptance by a specific CDN
also depends on that CDN having registered your key, which is a human process outside any
tool's control.

Python 3.9+, MIT, one runtime dependency.

```bash
pip install wingfoot     # or: uv tool install wingfoot
wingfoot demo
```

Repo: **https://github.com/AmirF194/wingfoot**

On the roadmap: recognizing Cloudflare and Akamai specific rejection signals in `doctor`,
`aiohttp` support, and a TypeScript port. If you are running agents that are getting
blocked right now, I especially want to hear which failure you hit and what the response
looked like — those are exactly the cases `doctor` should learn to name.

The web is going to keep asking bots for ID. Might as well carry one.
