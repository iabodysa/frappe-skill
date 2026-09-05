---
name: lazy
description: `_()` resolves against `local.lang` at call time, so a module body freezes the English string at import, and `_lt` is the only form that survives to render time.
triggers: ["_lt", "_LazyTranslate", "Cannot make dict for single fieldname", "_lt lazy translation", "translated string frozen at import", "the label is stuck in english no matter what language i pick", "some text on the page never switches language for anyone", "why is one button still english when everything around it is translated", "i added the translation and it still shows the english word", "the dropdown choices stay in english but the rest of the form translates", "the default value of a field is never translated", "comparing a translated value blows up with not implemented", "sorting a list of translated labels crashes", "checking if a translated string equals something raises an error", "the text translates in one place and not in another with the same wording", "nothing in the log explains why this one string never translates"]
product: frappe
---

# Translating in module scope

## paths

frappe/__init__.py — _, _lt
frappe/types/lazytranslatedstring.py — _LazyTranslate

## rules

MUST call `_lt` for a string built in module scope — a module constant, a class attribute, a default argument, a decorator argument, a dict written at import.
MUST call `_()` inside the function that runs per request, where `local.lang` is already set.
NEVER compare or sort a `_LazyTranslate`; `__eq__` and `__lt__` raise `NotImplementedError`.
MUST branch on the untranslated source string and keep the lazy value for display alone.
NEVER read an untranslated label as a missing translation before checking whether the string was built at import.

## values

`_()` returns: `str`, resolved once at the call
`_lt` returns: `_LazyTranslate`, resolved on `__str__`
language read from: `local.lang`, defaulted to `en` when unset
supported on `_LazyTranslate`: `__str__`, `__repr__`, `__add__`, `__radd__`
raises on `_LazyTranslate`: `__eq__`, `__lt__` and every comparison built on them

## how

A module body runs once, at import, before any request has set a language, so `_()` there takes the
default and returns the English string forever. Nothing raises and nothing logs; the label simply
stays English for every user in every language. That makes it the one translation failure that no
error report will ever name.

`_lt` moves the resolution to the moment the value is rendered by returning an object that calls `_()`
from `__str__`. The cost is that the object is not a string: concatenation works, comparison raises on
purpose so a silent `False` cannot hide, and anything that keys, sorts or matches on the value must use
the source string instead.

Ask of any `_()` call: does the line run per request? If it runs at import, it is the wrong function.
