---
name: fetch-from
description: fetch_from keeps only the last segment of a dotted path and reads that field on the doctype the local link field points to directly, never through a second link on the target document.
triggers: ["fetch_from", "set_fetch_from_value", "a two hop fetch", "fetch a field from a linked document's own link", "fetch_from dotted path", "my fetch_from with two dots does not populate", "fetch through a link on the linked doctype", "grandparent field will not fetch onto the child"]
product: frappe
---

# Fetch from

## paths

frappe/model/base_document.py — BaseDocument.set_fetch_from_value

## rules

MUST expect `df.fetch_from` to resolve through `df.fetch_from.split(".")[-1]` — only the last segment names the field read.
MUST expect that field to be looked up on the doctype the LOCAL link field points to, never on a doctype reached through a second link on that target.
NEVER write a `fetch_from` string of the shape `link_a.link_b.field` expecting it to walk two hops; `set_fetch_from_value` reads one hop and the middle segment is discarded, not traversed.
MUST reach a grandparent field with a Python hook — `validate` or a client script — when the source field sits behind a second link.

## how

`fetch_from` takes the local link field's target doctype and one field name on it; the string in between the first and last dot carries no meaning to the resolver, so a value only reachable through an intermediate linked document is invisible to the property and has to be moved by code.
