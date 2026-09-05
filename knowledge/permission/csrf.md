---
name: csrf
description: A Guest session carries no csrf_token, so validate_csrf_token returns without checking anything and allow_guest=True on a POST is CSRF-exempt by accident.
triggers: ["HTTPRequest.validate_csrf_token", "UNSAFE_HTTP_METHODS", "Session.start", "get_csrf_token", "generate_csrf_token", "Invalid Request", "Login with username and password is not allowed.", "Login not allowed at this time", "csrf token missing for guest", "allow_guest csrf exempt", "an outside website can post to my public endpoint", "random records are being created by someone who is not logged in", "we are getting spam submissions from a form we did not build", "is my public method safe from another site posting to it", "how do i protect an endpoint that guests are allowed to call", "the public endpoint writes data and nobody checks who called it", "anonymous visitors can trigger our write method and it is terrifying", "i get invalid request when posting from my script", "my post fails with invalid request but the get works fine", "why does the token check pass for logged out visitors", "do i need extra checks on a method open to everyone"]
product: frappe
---

# CSRF

## paths

frappe/auth.py — HTTPRequest.validate_csrf_token, UNSAFE_HTTP_METHODS
frappe/sessions.py — Session.start, get_csrf_token, generate_csrf_token

## rules

MUST treat every `@frappe.whitelist(allow_guest=True)` method that writes as reachable by a cross-site form POST.
MUST put the authority check inside the method — a shared secret, a signed payload, a rate limit — because validate_csrf_token returns before comparing anything when the session carries no csrf_token.
NEVER read the missing exemption decorator as proof a guest write is protected; validate_csrf_token exits on the first true condition in an or-chain, and an empty saved token is one of those conditions.
MUST prefer allow_guest on a READ and close the write behind a real session; a guest write is the shape that needs its own proof.

## how

validate_csrf_token drops the request through unchecked as soon as one of several conditions holds, and an empty saved_token is among them. Session.start skips insert_session_record for the Guest sid, so no session row and no csrf_token ever get generated for a Guest request. A Guest therefore reaches validate_csrf_token with saved_token empty, the check short-circuits, and the function returns before it ever compares a token. Nothing decorates the endpoint as exempt — the exemption is the absence of a token, so a grep for an exemption finds nothing and the method still writes unauthenticated.
