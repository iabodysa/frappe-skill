---
name: cache-decorators
description: redis_cache caches a return value under a key hashed from the call's own arguments, request_cache and site_cache scope to the request or the process, and none of the three expresses a caller-driven is-it-cached check or a success-only write.
triggers: ["request_cache", "site_cache", "redis_cache", "RedisWrapper", "redis_cache vs request_cache", "cache decorator scope", "the cached value never updates even after i change the data", "my function keeps handing back the same old answer", "why does it still show stale data after the record changed", "one server has the fresh number and the other has the old one", "two users get different answers for the same lookup", "why do my workers disagree about the same value", "a failed lookup got remembered and now everyone gets nothing back", "an empty result stuck around for an hour and broke the page", "how do i check whether something is already cached before i call it", "how do i clear the remembered answer for one function", "the same slow call runs over and over inside a single page load"]
product: frappe
---

# Cache Decorators

## paths

frappe/utils/caching.py — request_cache, site_cache, redis_cache
frappe/utils/redis_wrapper.py — RedisWrapper

## rules

MUST choose request_cache for a call repeated within one request, because it stores in frappe.local.request_cache and clears when the request ends.
MUST choose site_cache for a call repeated across requests on one process, because it stores in a process-local dict and is not shared between workers; MUST use frappe.cache when the value needs to be shared across workers.
MUST choose redis_cache(ttl=...) to cache the return value of a pure call — same arguments, same answer, expensive to recompute — because it hashes the call's own arguments into the key and ships clear_cache(), user= and shared= for the caller to use.
NEVER convert a frappe.cache.set_value call that stores a fact keyed by an entity — a flag, a counter, a one-shot marker — to redis_cache; there is no function whose return value the fact is, so the decorator cannot express it.
NEVER convert a module that exposes its own is-it-cached check and its own bounded-fetch entry points to redis_cache; the decorator offers exactly one operation, call and maybe answer from the cache, with no way to ask whether a value is already cached and no way to say answer from the cache or give up.
MUST read a cache written by hand that writes only on its success path as expressing something redis_cache cannot: redis_cache writes unconditionally, so a failing upstream call has its None cached and served to every caller until the TTL expires.
MUST check frappe.utils.redis_wrapper.RedisWrapper's base class before concluding frappe.cache lacks a capability, because it subclasses redis.Redis directly, so eval, a pipeline and setnx are all present as inherited methods a grep for a local def will not find.

## values

request_cache stored in: frappe.local.request_cache, cleared at request end
site_cache stored in: frappe.utils.caching._SITE_CACHE, per process, not shared across workers
redis_cache key: func_key + "::" + hash of (args, kwargs)
redis_cache params: ttl default 3600, user for per-session isolation, shared for cross-site isolation
redis_cache write: unconditional — val = func(...), then set_value(...), with no test of what came back

## how

The three decorators differ by scope, not by strength: request, process, or redis, in that order, and the widening from one to the next is not "more caching" than the last — request_cache and site_cache exist because paying redis round trips for something that already dies with the request or the worker is waste, not because they are weaker forms of redis_cache.

What none of the three can do is answer a caller's own question. redis_cache is called, and it may answer from the cache or run the function — that is the entire interface. A caller that needs to ask whether the value is already cached before spending a call, or that needs "answer from the cache or refuse" as a branch distinct from "answer from the cache or compute", is expressing something the decorator has no parameter for, and rebuilding the call-and-cache shape around it is not the same defect as caching the same call by hand.
