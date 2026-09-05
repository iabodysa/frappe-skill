---
name: stdlib-wrappers
description: now_datetime, as_json and parse_json change behaviour relative to their stdlib equivalents, and most other stdlib reaches already have a frappe.utils wrapper.
triggers: ["now_datetime", "now", "today", "getdate", "add_days", "add_months", "get_system_timezone", "as_json", "parse_json", "generate_hash", "Cannot make dict for single fieldname", "frappe utility functions wrapping python stdlib", "now_datetime vs datetime.now", "the timestamps are off by a few hours from what the users see", "why does the saved time not match the time shown on screen", "how do i get the current time in the site timezone and not the server one", "everything is coming out in indian time and we are not in india", "converting my data to json blows up on a date field", "the serializer crashes when i pass it a record object", "how do i turn a document into json without an error", "the incoming parameter is sometimes text and sometimes already an object", "after i swapped the json call every stored signature stopped matching", "the cached keys all changed and nothing raised an error", "what should i use to generate a random token or id", "is there an existing helper for this or do i import the standard library"]
product: frappe
---

# Stdlib Wrappers

## paths

frappe/utils/data.py — now_datetime, now, today, getdate, add_days, add_months, get_system_timezone
frappe/__init__.py — as_json, parse_json, generate_hash

## rules

MUST take every clock and calendar value from now_datetime, now, today, getdate, add_days or add_months; NEVER call datetime.now, datetime.today, datetime.utcnow or date.today, because now_datetime converts a UTC reading into the site timezone while the stdlib call reads the server clock, and nothing raises when the two zones differ.
MUST set time_zone in System Settings, because get_system_timezone falls back to Asia/Kolkata when it is unset.
MUST serialise with frappe.as_json, which encodes Frappe types and datetime through json_handler; json.dumps raises on a Document and on a date.
MUST decode a request parameter with frappe.parse_json, which returns a non-string value unchanged, and MUST delete the isinstance(value, str) check it replaces.
NEVER replace a json.dumps call whose bytes feed a hash key or a request signature with as_json; as_json writes indent=1 and different separators, so the substitution changes every stored hash and every accepted signature without raising.
MUST call frappe.generate_hash(txt=None, length=56) in place of hashlib, random or uuid for an id or a token.
MUST search frappe/utils/ for an existing helper before importing a stdlib module into a frappe app; re and base64 have no wrapper and MUST be imported directly.

## values

now_datetime: a UTC reading converted to the system timezone, tzinfo stripped
system timezone fallback: Asia/Kolkata, when System Settings time_zone is unset
as_json defaults: indent=1, separators (",", ": ")
also wrapped: os.path join for app or site files by frappe.get_app_path / get_site_path, requests by frappe.integrations.utils.make_post_request / make_get_request, float/int by flt / cint / cstr, csv/xlsx by frappe.utils.csvutils / xlsxutils, a cache or a lock by frappe.cache and frappe.utils.synchronization

## how

Two wrappers change behaviour rather than merely naming a call: now_datetime resolves the site's own timezone before an app ever sees a value, and as_json serialises types json.dumps cannot touch at all. Treat both as the site's decision, not the process's — the same code produces different clock readings on a server in one zone serving a site configured for another, and produces a TypeError from json.dumps where as_json would have succeeded.

The place this reverses is a byte-exact contract: a hash key or a signature computed over json.dumps output is computed over particular bytes, and as_json does not reproduce them. Ask what consumes the string before converting a json.dumps call, and never run a blanket rewrite across a tree for this reason alone.
