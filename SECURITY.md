# Security Policy

wingfoot signs and verifies HTTP requests with Ed25519 keys, so the correctness
of its cryptography and key handling is a security concern. If you find a
vulnerability, please report it privately so it can be fixed before it is
disclosed publicly.

## Supported versions

wingfoot is in alpha (0.x). Fixes land on the latest release only; there are no
backports. Please test against the newest version before reporting.

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |
| < 0.1   | :x:                |

## Reporting a vulnerability

Please **do not open a public issue** for a security problem.

Report it privately through GitHub's private vulnerability reporting:

- Open <https://github.com/AmirF194/wingfoot/security/advisories/new>, or
- On the repository, go to the **Security** tab and choose **Report a vulnerability**.

Include what you can:

- the version (`wingfoot --version`) and your OS / Python version,
- a description of the issue and its impact,
- steps to reproduce, ideally a minimal example.

Please redact any real private keys or signatures from your report.

### What to expect

- We aim to acknowledge a report within **5 days**.
- We will confirm the issue, work on a fix, and keep you updated on progress.
- When a fix ships, we will publish an advisory and credit you, unless you would
  rather stay anonymous.

## Scope

Especially worth reporting:

- signature forgery or verification bypass — a request that verifies when it
  should not, or one that fails to verify when it should,
- mishandling of private keys or the on-disk identity,
- anything that lets one agent impersonate another agent's `keyid`.

Because wingfoot's job is proving identity, the RFC 9421 signature base and
parameter handling in [`src/wingfoot/rfc9421.py`](src/wingfoot/rfc9421.py) are
the most sensitive code paths.
