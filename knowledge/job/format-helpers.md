---
name: format-helpers
description: fmt_money reads two site defaults and the Currency record before it formats, comma_and quotes each item before translating it so the quoted key never matches a row, and get_url_to_form builds an absolute URL whose host follows the request.
triggers: ["fmt_money", "comma_and", "comma_or", "comma_sep", "get_url_to_form", "get_absolute_url", "get_url", "quoted", "slug", "get_number_format_info", "number_format_info", "hide_currency_symbol", "format money in python", "link to a document in an email", "the amount prints with no currency sign at all", "why is the currency symbol missing from my totals", "the symbol shows on the wrong side of the number", "the digits are grouped in twos instead of threes", "the amount has too many decimal places", "the joined list keeps showing english words after translation", "turning items into a sentence leaves them untranslated", "the link inside my email points at a loopback address", "the link i sent people opens the wrong address", "how do i build a link to a record that works from an email", "how do i print a number as money in a script"]
product: frappe
---

# Format helpers

## paths

frappe/utils/data.py — fmt_money, comma_and, comma_or, comma_sep, get_number_format_info, number_format_info, get_url_to_form, get_url_to_list, get_absolute_url, get_url, quoted
frappe/desk/utils.py — slug

## rules

MUST expect `fmt_money` to return a string, and NEVER to compare or add its result; it is display output.
MUST pass `format` when the output must not follow the site, because it otherwise takes the `number_format` default and falls back to `#,###.##`.
MUST pass `precision` when the output must not follow the site, because it otherwise takes the `currency_precision` default and then the precision that the number format itself declares.
MUST expect `#,##,###.##` to group everything above the last three digits in twos rather than threes.
MUST pass `currency` to get a symbol at all, and MUST expect that argument to read `symbol`, `symbol_on_right` and `fraction_units` off the Currency record and to place the symbol on the side that record names.
MUST expect the symbol to be dropped whenever the global default `hide_currency_symbol` is `Yes`, so a currency argument alone does not guarantee a symbol in the output.
MUST expect the symbol to be translated before it is joined to the amount.
MUST pass a list or a tuple to `comma_and`; any other value is returned unchanged, so a string arrives back whole rather than joined.
MUST expect `comma_and` to return the empty string for an empty list and the single item unquoted for a list of one, and to reach the `{0} and {1}` pattern only from two items up.
MUST pass `add_quotes=False` when the items are already translated, because the quotes are added before the translation lookup, so a quoted item is looked up with its quotes and never matches a row.
MUST expect only the items before the last to go through the translation lookup at all.
MUST use `comma_or` where the sentence means a choice; it is the same function under the `{0} or {1}` pattern.
MUST use `get_url_to_form` for a link that leaves the site — an email, a notification, a message — because it returns an absolute URL, and `get_absolute_url` for a link inside a page, because that one returns the path alone.
MUST expect the host in that URL to come from the `host_name` key in the site config first, then from the request's own host header, then from the site name, so a link built inside a request follows whatever host the client asked for.
MUST set `host_name` in the site config for links built in a background job, because off a request the fall-back chain ends at the Website Settings subdomain and then at a loopback address.
MUST expect the doctype segment to be lower-cased with its spaces turned into hyphens and both segments to be percent-encoded, so the name never needs escaping by the caller.

## values

fmt_money returns: `str`
number format source: the `number_format` default, else `#,###.##`
precision source: the `currency_precision` default, else the format's own precision
currency reads: `symbol`, `symbol_on_right`, `fraction_units`
symbol suppressed by: the global default `hide_currency_symbol` set to `Yes`
comma_and patterns: `{0} and {1}`, and `{0} or {1}` for comma_or
comma_and on a non-sequence: the argument, unchanged
quoting: `'item'`, applied before the translation lookup
form url: `/app/<doctype lower-cased, spaces hyphened>/<name>`, percent-encoded
absolute against: config `host_name` or `hostname`, else the request host header, else the site name, else the Website Settings subdomain, else `http://127.0.0.1`

## how

All three helpers read state rather than only their arguments. `fmt_money` reads two defaults and one Currency record, so the same amount formats differently on two sites and the currency lookup is a query. `get_url_to_form` reads the config and the request, so the link it returns is only as trustworthy as the host header when the config names no host — which is why a job that emails links needs `host_name` set.

`comma_and` is a sentence builder, not a joiner. It translates the pattern and the leading items, which is what makes the quoting order matter: quote the items yourself only when they are proper nouns, and pass `add_quotes=False` for anything that has a translation.
