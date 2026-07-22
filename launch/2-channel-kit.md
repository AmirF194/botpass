# Channel kit — copy/paste per platform

Same project, different framing per audience. Never cross-post the identical text; each
community can smell it, and it is the fastest way to get flagged.

---

## 1. Hacker News (highest upside — do this one properly)

**Post as a Show HN. Tuesday–Thursday, 8–10am ET.** Submit the GitHub repo URL directly,
not the blog post.

### Title options

Pick one. HN hates hype, so no adjectives, no "revolutionary", no emoji.

1. `Show HN: Wingfoot – find out why your signed AI agent still gets a 403`
2. `Show HN: Wingfoot – Web Bot Auth identity and diagnostics for AI agents`
3. `Show HN: A doctor command for Web Bot Auth (RFC 9421) signatures`

I would use **#1**. It names a pain instead of a category.

### First comment (post immediately after submitting)

> Author here.
>
> Background: sites increasingly block unrecognized automated traffic by default, and the
> industry answer is Web Bot Auth — a profile of RFC 9421 HTTP Message Signatures. Your
> agent signs each request with an Ed25519 key, publishes the public key as a JWKS at
> `/.well-known/http-message-signatures-directory`, and the verifier checks the signature
> instead of trusting your User-Agent string.
>
> Signing is easy. What cost me a weekend was that every failure returns the same bare
> `403`: expired signature, 40 seconds of clock skew, a directory that returns HTML
> because the host redirected `/.well-known/`, a missing `tag="web-bot-auth"`, a key that
> is not actually listed in the directory you are pointing at. One status code, a dozen
> causes, no diagnostics.
>
> So the core of this is `wingfoot doctor <url>`, which tests each link separately and
> names the broken one. It also deliberately refuses to claim success when a signed
> request returns 200 but the unsigned one did too — that proves nothing about whether
> the signature was honored.
>
> `uvx wingfoot demo` runs an unsigned and a signed request against a reference verifier
> in-process, offline, no setup, if you just want to see the 403→200 flip.
>
> Honest status: alpha (0.1.2). Signing, verification, directory and doctor work and are
> tested against a reference verifier. Doctor proves *your* side is correct — actual
> passage through a given CDN also requires that CDN to have registered your key, which
> is still a manual web form with a human behind it at every provider.
>
> Python 3.9+, MIT, only runtime dep is `cryptography`. Happy to answer anything about
> RFC 9421 or the directory draft.

### Be ready for these questions

- *"Why not just use `http-message-signatures`?"* — Fair, and say so plainly: that library
  is a good general RFC 9421 implementation. Wingfoot is the Web Bot Auth profile plus the
  parts around it — key directory hosting, the thumbprint keyid, registration packets, and
  the diagnostics. Different layer, not a competitor.
- *"Cloudflare already ships a library."* — Yes, in TypeScript and Rust. This is Python,
  where most agent code lives, and it is a CLI as much as a library.
- *"Does this actually get you past Cloudflare?"* — Do not overclaim. The true answer is in
  the first comment already: it makes your side provably correct; passage requires
  registration. Overclaiming here is how launches die in the comments.
- *"Isn't this just re-inviting the scrapers everyone is blocking?"* — Good faith answer:
  the point is making bot traffic *accountable*. An identified agent can be rate-limited,
  allowed, or banned deliberately. Anonymous traffic can only be guessed at.

---

## 2. Reddit

Different subreddit, different angle. Space these out by several days.

### r/Python — lead with the package

**Title:** `wingfoot: a CLI + library for Web Bot Auth (RFC 9421 request signing), with a doctor that explains 403s`

Lead with `uvx wingfoot demo`, the one-line `requests`/`httpx` integration, and the fact
that the only runtime dependency is `cryptography`. This sub rewards small dependency
trees and dislikes marketing tone.

### r/LocalLLaMA and r/AI_Agents — lead with the pain

**Title:** `If your agent started getting 403s this year, this is why — and how to give it an ID`

These are the people actually hitting the wall. Explain Web Bot Auth first, and mention
the tool near the end. Teach-first is not a trick here; it is the only thing that works in
these subs.

### r/webdev — flip the perspective

**Title:** `Web Bot Auth from the other side: what you're actually verifying when a bot signs its requests`

This audience *runs the sites*. They care about `wingfoot verifier` and `wingfoot serve` —
being able to stand up a reference verifier and see what a signed request looks like
before deciding a policy.

### r/programming — protocol angle only

**Title:** `How Web Bot Auth works: signing HTTP requests so bots can prove identity (RFC 9421)`

Link the write-up, not the repo. This sub is hostile to anything that reads as promotion.

---

## 3. X / Twitter thread

Post the terminal output as an image or the GIF at `media/wingfoot-doctor.gif` — the
403→200 flip is the whole pitch and it is visual.

> 1/ In 2026 the web stopped believing User-Agent strings.
>
> Cloudflare, Akamai, Fastly and AWS WAF block unrecognized bots by default. If you run an
> AI agent, you have probably met the bare 403 with no explanation.
>
> The fix is an ID card. Here is how it works. 🧵

> 2/ It's called Web Bot Auth — RFC 9421 HTTP Message Signatures, applied to bots.
>
> Three headers and one file:
> • Ed25519 keypair, private key stays with your agent
> • public key hosted as JWKS at /.well-known/http-message-signatures-directory
> • every request signed with Signature-Agent / Signature-Input / Signature

> 3/ Verifier fetches your key file, finds the key by its thumbprint, checks the math.
>
> Now "I am this bot" is proof instead of a claim.

> 4/ Signing is the easy part.
>
> The hard part: every failure returns the same 403.
>
> Expired signature? 403. Clock 40s fast? 403. Directory serving HTML? 403. Missing
> tag="web-bot-auth"? 403.
>
> One bit of feedback, a dozen possible causes.

> 5/ So I built wingfoot, and the command that matters is `doctor` — it checks each link
> separately and names the broken one.
>
> It also won't claim success if the signed request got a 200 but so did the unsigned one.
> That difference is the only real signal.
> [GIF]

> 6/ Try it in one line, offline, nothing to configure:
>
> uvx wingfoot demo
>
> Python 3.9+, MIT, one dependency.
> https://github.com/AmirF194/wingfoot
>
> Alpha and honest about it. If your agent is getting blocked, tell me what the response
> looked like.

---

## 4. Medium — lower priority, and here is why

Be realistic: Medium is a weak channel for developer tools in 2026. The big engineering
publications have faded, most dev traffic goes to dev.to / HN / Reddit, and Medium's
paywall actively works against a "run this command" post.

If you post there anyway, do it **last**, as a canonical-tagged repost of the dev.to
article pointing back at the original so you do not split the SEO. Do not write a separate
piece for it.

---

## 5. Places that are not social media but convert better

These matter more than a second Medium post and almost nobody does them:

- **The Cloudflare community forum and Akamai forums** — answer existing threads from
  people whose agents are blocked. Real questions, real intent.
- **Existing GitHub issues** — search `web-bot-auth 403` and `Signature-Agent` across
  GitHub issues in agent frameworks. People are stuck right now.
- **`cloudflare/web-bot-auth`** — open a friendly issue or discussion noting a Python
  implementation exists for the ecosystem list. The maintainers are the audience.
- **The IETF working group mailing list** — an implementation report from a real
  independent implementer is genuinely welcome there, and it is the highest-credibility
  room in this whole topic.
- **Agent framework docs** — LangChain, CrewAI, browser-use and similar have "deployment"
  or "troubleshooting" pages. A short PR adding a note about signed identity is durable
  traffic that never expires.
- **awesome-lists** — awesome-python, and any AI agent list.
