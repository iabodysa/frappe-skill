---
name: use-call
description: The params passed to submit are stored in submitParams and sent by every later call until reset, and an error thrown in beforeSubmit reaches no ref the caller reads and stops nothing.
triggers: ["useCall submit params stay after first submit", "useCall error handling", "the filters stopped updating after i clicked the button once", "it keeps sending the same old values on every later request", "why is my request using yesterday's filter instead of the new one", "my validation check throws but the request goes out anyway", "the check that runs before sending does not stop anything", "how do i actually block a request before it is sent", "i see an error in the console but nothing shows in the interface", "the failure message never reaches the screen", "old data shows up before the new response arrives", "how do i go back to the reactive parameters after passing them by hand once"]
product: frappe-ui
---

# useCall

## paths

src/data-fetching/useCall/useCall.ts — useCall, computedParams, submit, reset, execute
src/data-fetching/idbStore.ts — idbStore

## rules

MUST expect `computedParams` to read `submitParams` first and to fall back to the `params` option, function or value, only while `submitParams` is falsy.
MUST expect `submit(params)` to write `submitParams` whenever the argument is not null, and MUST expect nothing but `reset()` to clear it.
MUST call `reset()` to hand control back to a reactive `params` option after any `submit` that carried an argument, because every later execute keeps sending the stored values.
MUST expect `submit` to await `beforeSubmit`, to catch what it throws, to log it with `console.error`, and to continue into the request with no early return.
MUST expect the thrown error to be stored in a ref the returned object does not carry, so a rejecting validation hook shows on nothing the caller can read.
MUST expect the returned `error` to be fixed at setup by a ternary that runs while the `beforeSubmit` error is still null, so it always resolves to the fetch error.
MUST validate before calling `submit` and MUST NOT rely on `beforeSubmit` to block a request.
MUST expect `submit` to call `execute()` itself only while `refetch` is false.
MUST expect `fetch` and `reload` to be the same function as `execute`.
MUST expect a cache key to serve a stored response through `data` while the call is loading or unfinished.

## values

params order: `submitParams`, then a `params` function, then a `params` value, then an empty object
clears `submitParams`: `reset()` only
beforeSubmit throw: logged, stored in a ref that is not returned, request proceeds
returned error: bound once at setup to the fetch error
GET url: base plus the params as a query string

## how

`submit` looks like a one-shot call and changes the composable for the rest of its life. Passing params once makes `submitParams` the source of every later request instead of the reactive `params` option, so a filter that stopped updating after the user pressed a button is this, not a broken watcher. Either always pass params to `submit`, or never — mixing the two is what produces the stale request.

`beforeSubmit` runs before the request and never stops it. Read its name as "run this first", and put anything that must stop the request in the caller before `submit` is reached.
