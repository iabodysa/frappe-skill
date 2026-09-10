---
name: login-attempt-tracker
description: LoginAttemptTracker is a Redis-hash failed-attempt counter keyed by an arbitrary string, not restricted to login or username use.
triggers: ["LoginAttemptTracker", "lock the account after failed attempts", "N wrong attempts locks for M minutes", "OTP attempt lockout", "PIN attempt lockout", "reuse the login lockout counter for something else", "a general purpose failed attempt counter", "max_consecutive_login_attempts", "lock_interval"]
product: frappe
---

# Login attempt tracker

## paths

frappe/auth.py — LoginAttemptTracker

## rules

MUST construct `LoginAttemptTracker(key, max_consecutive_login_attempts, lock_interval)` with any string as `key`; the class stores it as `self.key` and is not restricted to a username.
NEVER read `user_name` as the supported parameter; it is kept only as a deprecated alias for `key` and emits a deprecation warning.
MUST reuse this class for any "N consecutive wrong attempts locks the key for M minutes" requirement — an OTP id, a PIN attempt, a per-device counter — instead of writing a new Redis counter.

## values

constructor: key, max_consecutive_login_attempts=3, lock_interval=300 seconds
deprecated: user_name keyword, aliased to key
backing store: Redis hash

## how

The class carries no reference to the User doctype or to the login form; it is a generic "count failures against a key, lock the key past a threshold" primitive that the login flow happens to be the first caller of.
