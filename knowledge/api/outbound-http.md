---
name: outbound-http
description: Every make_*_request call shares one session whose Retry list is [500] with no backoff, so a 429 or a 503 raises on the first response and a 500 is repeated five times in a burst.
triggers: ["make_request", "make_get_request", "make_post_request", "make_put_request", "make_patch_request", "make_delete_request", "get_request_session", "call an external api and retry", "http request retry and backoff", "the outside service says we are sending too many requests", "we keep getting rate limited when calling a partner api", "why does one failed call turn into six calls to the vendor", "our integration hammers their server the moment it goes down", "the call to the other system fails instantly instead of trying again", "why does a temporary outage of the provider break my call right away", "the gateway is down and we give up on the first try", "the request comes back empty and my code treats it as an error", "how do i tell an empty successful reply from a failed one", "nothing came back from the outside call but there was no error", "the error log fills up with the same outbound failure over and over", "a call to another system throws and nobody catches it"]
product: frappe
---

# Outbound HTTP

## paths

frappe/integrations/utils.py — make_request, make_get_request, make_post_request, make_put_request, make_patch_request, make_delete_request
frappe/utils/__init__.py — get_request_session

## rules

MUST read the retried status list as `[500]` and nothing else; a 429, a 502, a 503 and a 504 raise on the first response.
NEVER expect a backoff; `Retry` is built with no `backoff_factor`, so the attempts leave immediately after one another and a rate-limited provider sees six requests in a burst.
MUST expect a row in Error Log for every failure; `make_request` calls `frappe.log_error()` and then re-raises, so the caller both logs and throws.
MUST branch on the response shape rather than the status: a JSON content type returns a parsed object, `text/plain; charset=utf-8` returns a `parse_qs` dict, any other content type with a body returns the raw text, and an empty body or a missing content type returns `None`.
MUST catch the exception at the call site when the outside service is allowed to be down, because nothing above `make_request` does.
MUST call `get_request_session` with an explicit `max_retries` when a provider must not be hammered; the parameter exists and every caller in frappe takes the default.
MUST read `frappe.flags.integration_request` as holding the last response object, set before `raise_for_status` runs.

## values

retried statuses: 500
attempts: 1 plus 5 retries
backoff: none
success test: `raise_for_status`
parsed as query string: `text/plain; charset=utf-8`
parsed as JSON: a content type starting `application/` whose first segment ends `json`
returns None: empty body, or no content-type header
last response: `frappe.flags.integration_request`

## how

There is one outbound function. The five verb helpers all call `make_request`, and `make_request` builds a fresh `requests.Session` per call through `get_request_session`, so the retry policy is not configurable per call site — it is the same policy everywhere unless a caller builds its own session.

That policy retries the one status a server sends when it has already failed, and does not retry the statuses that mean "come back later". Read this backwards when choosing where to put your own retry: rate limiting and gateway errors need handling at your call site, because the session will not do it, and a 500 needs no handling at all, because it has already been attempted six times before you see the exception.

The return value is decided by the content type, not by the status, and every failure path is an exception. So a `None` return is a successful call with nothing in it, never a failure. Branching on a falsy return conflates an empty 204 with an error that would have raised.
