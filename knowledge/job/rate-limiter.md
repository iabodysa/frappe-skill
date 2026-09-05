---
name: rate-limiter
description: The rate_limit decorator counts with a read-then-write race and keys its limit on cmd, so a parallel flood can hold the counter near zero and a limit spanning several endpoints cannot be expressed by it.
triggers: ["rate_limit", "RateLimitExceededError", "Either key or IP flag is required.", "You hit the rate limit because of too many requests. Please try after sometime.", "rate limit decorator race condition", "api rate limiting", "the rate limit does not block anything under heavy traffic", "flooding the endpoint gets through without being throttled", "why does the throttling stop working exactly when i am attacked", "the counter stays near zero while requests pour in", "i want one limit across all endpoints not per endpoint", "how do i limit a user across the whole api instead of one call", "each endpoint has its own separate counter and that is not what i want", "the limit can be bypassed by hitting a different endpoint", "how do i make the request counting exact", "the throttle count is wrong when requests arrive at the same time"]
product: frappe
---

# Rate Limiter

## paths

frappe/rate_limiter.py — rate_limit, RateLimitExceededError

## rules

MUST read the counter sequence as get, then setex when empty, then incrby, because a request whose get saw an empty key can reset it to zero after another request already filled the window, erasing that window's count.
MUST expect the limit to go quiet under a parallel flood rather than to fire harder, because the race holds the counter near zero exactly when the flood is heaviest.
MUST expect the cache key to be rl: plus cmd plus identity, so the limit is per endpoint; a limit that must be spent once per actor or per address across every entry point cannot be expressed by the decorator.
MUST use an atomic INCR followed by a conditional EXPIRE in place of get/setex/incrby for a custom counter that needs the count to be exact, because INCR returns the post-increment value, so only the caller that turns 0 into 1 is the one that sets the TTL.
NEVER leave a rebuilt rate limiter unexplained; name which of the two weaknesses — the race, or the per-cmd key — is being worked around, because a custom limiter with neither reason stated is a rebuild, not a fix.

## values

cache key: rl: + frappe.form_dict.cmd + : + identity
counter sequence: get, setex(key, seconds, 0) when empty, incrby(key, 1)
throw: frappe.RateLimitExceededError when the incremented value exceeds the limit

## how

The decorator is not atomic across its three redis calls, so its count is a target for a race rather than a guarantee: two requests can both see an empty key, both reset it, and the window's true count is lost between them. A single INCR with a conditional EXPIRE closes that gap in one round trip, because INCR itself returns the value it produced, so only the request that turns 0 into 1 is the one that sets the expiry — nothing is read before it is written.

The key's shape is a separate weakness from the race. Binding the limit to cmd means every endpoint gets its own counter; a limit meant to bound one actor across the whole API, or one bound to a server-resolved identity rather than a request field, needs a different key scheme the decorator does not offer.
