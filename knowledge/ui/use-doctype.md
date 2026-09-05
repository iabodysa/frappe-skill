---
name: use-doctype
description: delete, runDocMethod and runMethod each keep one url ref per instance, so a second submit before the first resolves moves the loading state onto the newer call.
triggers: ["useDocType runMethod loading state", "second submit before first resolves", "the spinner shows on the wrong row when i click two buttons quickly", "why does the first row stop showing loading when i click a second one", "clicking approve on several rows at once and only the last one spins", "the loading indicator jumps to another row on its own", "i click delete on two records and one of them never shows it is working", "does firing the same action on many rows at the same time break the loading state", "the button stays stuck as if nothing happened after a rapid second click", "the error from my check does not appear anywhere in the form", "why do i get the wrong error message back when a check fails", "the deleted record is gone from the server but still sitting in my list", "how do i run the same action on a whole table of rows safely"]
product: frappe-ui
---

# useDoctype

## paths

src/data-fetching/useDoctype/useDoctype.ts — useDoctype, useInsert, useDelete, useSetValue, useRunDocMethod, useRunMethod, isLoading
src/data-fetching/useCall/useCall.ts — useCall
src/data-fetching/docStore.ts — docStore
src/data-fetching/useList/listStore.ts — listStore

## rules

MUST expect `useDelete`, `useRunDocMethod` and `useRunMethod` each to hold one `url` ref and to overwrite it in `submit` before delegating to one shared `useCall`.
MUST expect `loading`, `data` and `error` on that instance to be one set of refs shared by every request rather than one set per request.
MUST expect `isLoading(name, method)` to compare the current url to the expected one, so the first call's row loses its loading state the moment a second submit rewrites the url.
MUST build a fresh `useDoctype` per row where rows call the same method concurrently, or MUST await each submit before firing the next.
MUST expect a `validate` returning a message to reject the promise with that error and to write it into the composable's error, which a computed prefers over the call's own error.
MUST expect the delete success handler to remove the document from `docStore` and the row from `listStore`.

## values

delete url: the document endpoint for doctype and name
runDocMethod url: the document method endpoint for doctype, name and method
runMethod url: the doctype method endpoint for doctype and method
shared per instance: `url`, `loading`, `data`, `error`
isLoading: loading and the url matching the expected one
validate: a returned message rejects before the request

## how

Each of these is one call object wearing a per-request interface. The url is a variable that `submit` sets and the request reads, which is correct for one call at a time and wrong the instant a list gives every row the same object. The symptom is cosmetic first — a spinner on the wrong row — and becomes real when a handler reads `data` for a response that belongs to another row.

The unit of concurrency is the composable instance. If two things can be in flight, build two.
