---
name: inbound-verification
description: verify_request authenticates a signed GET link and refuses any request carrying a body, so frappe verifies no inbound webhook and the app has to write that check itself.
triggers: ["get_signed_params", "get_secret", "verify_request", "_sign_message", "get_url", "get_signature", "verify_using_doc", "auth_webhook", "PushNotification._get_credential", "HTTPRequest.validate_csrf_token", "UNSAFE_HTTP_METHODS", "make_form_dict", "get_request_form_data", "Invalid Request", "Login with username and password is not allowed.", "Login not allowed at this time", "verify an incoming webhook request", "signed request verification", "the incoming webhook always fails the signature check", "we get an invalid link page instead of a webhook response", "why does the built in check reject every post we receive", "our signature never matches even though the secret is right", "the digest only matches sometimes depending on the payload", "anyone can post to our endpoint and we accept it", "is there anything stopping a stranger from faking a callback to us", "the receiving endpoint takes any payload without checking who sent it", "outside calls get blocked with a token error before reaching our code", "the provider gets a 403 when it tries to notify us", "how do i prove an incoming call really came from the provider", "rejected calls leave no trace so we cannot debug them", "the header the provider sends is never validated on our side"]
product: frappe
---

# Inbound verification

## paths

frappe/utils/verified_command.py — get_signed_params, get_secret, verify_request, _sign_message, get_url, get_signature, verify_using_doc
frappe/push_notification.py — auth_webhook, PushNotification._get_credential
frappe/auth.py — HTTPRequest.validate_csrf_token, UNSAFE_HTTP_METHODS
frappe/app.py — make_form_dict
frappe/api/v1.py — get_request_form_data

## rules

MUST read `verify_request` as a link verifier only; it requires `frappe.request.method == "GET"` and an empty `frappe.request.form` and `frappe.request.data`, so a signed POST fails both tests whatever its signature.
NEVER call `verify_request` from an endpoint that takes a body; a failure renders an "Invalid Link" HTML page through `frappe.respond_as_web_page` and returns `False`, so a caller that ignores the return value keeps running.
MUST pair `verify_request` with `get_signed_params`, which is what every caller in frappe does — unsubscribe, newsletter, workflow action and the two personal-data requests.
MUST expect one signing key for the whole site; `get_secret` reads `frappe.local.conf.secret` and falls back to the site encryption key.
MUST write the verification in the app, because nothing in frappe verifies an inbound body and an endpoint without one accepts a forged payload.
MUST read the raw bytes with `frappe.request.get_data()`, the way `get_request_form_data` does; a digest over `frappe.form_dict` covers a re-serialization and not what arrived, because `make_form_dict` parses the body into a dict on every request.
MUST compare with `hmac.compare_digest`, as `verify_request` does.
MUST declare the endpoint `@frappe.whitelist(allow_guest=True, methods=["POST"])`; a guest session holds no `csrf_token`, so `validate_csrf_token` returns on the falsy saved token before it compares anything.
MUST record the call with `create_request_log` so a rejected payload still leaves a row.
NEVER read the `X-Frappe-Webhook-Signature` header as something frappe can check; it is written on an outgoing request and read back nowhere.

## values

signing algorithm, link: HMAC-SHA512 hex, over the urlencoded params
signing key: site config `secret`, falling back to `encryption_key`
signature parameter: `&_signature=`
accepted verb: GET only
accepted body: none — `form` and `data` must both be empty
inbound endpoint in frappe: `frappe.push_notification.auth_webhook`
that endpoint's credential: a cache token under `push_relay_registration_token:<secret>`, held 600 seconds
that endpoint's refusal: HTTP 401 with an empty body

## how

Frappe has one HMAC verifier and it is built for a link in an email, not for a webhook. Its two extra tests — GET, and no body — are what make it a link verifier, and they are also what make it useless in a receiving endpoint: the very thing a webhook carries is the thing it rejects. So the framework verifies no inbound body at all.

The one inbound endpoint frappe declares shows the pattern it prefers instead of a signature. The site itself generates a secret, hands the relay a URL carrying it, and answers with a token it put in the cache for ten minutes. The caller proves nothing about the body; it proves it knows a value only this site handed out, and the window closes on its own.

When you do write a body verifier, the trap is which bytes you hash. Every request has already been parsed into `form_dict` by the time your function runs, and re-serializing that dict gives a different string from what the sender signed — different key order, different separators, different number formatting. Hash the raw request data, compare in constant time, and log the rejection, or a failed verification leaves no trace that anyone tried.
