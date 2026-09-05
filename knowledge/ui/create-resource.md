---
name: create-resource
description: A cache key returns the first caller's resource object with its own url and callbacks, and every option the later call passed is dropped without a message.
triggers: ["createResource", "cached", "getCacheKey", "fetch", "handleError", "reset", "update", "setData", "createResource cache key options ignored", "second createResource call ignored", "my second fetch call is hitting the wrong address", "why is the same data showing up in two different places", "the success callback i passed is never called", "two screens keep overwriting each other's loading spinner", "my error handler runs but the app still crashes with an unhandled rejection", "clicking the button throws an uncaught error even though i handle errors", "changing the address in the second call did nothing at all", "how do i stop two components from sharing the same fetched data", "old data appears before the request finishes", "why does the call still reject after i already showed the error message"]
product: frappe-ui
---

# createResource

## paths

src/resources/resources.js — createResource, cached, getCacheKey, fetch, handleError, reset, update, setData
src/resources/local.ts — saveLocal, getLocal, deleteLocal
src/utils/config.ts — getConfig

## rules

MUST expect `createResource` to look up `cached[cacheKey]` before it reads any other option, and to return that object unchanged when the key is taken.
MUST expect `url`, `transform`, `onSuccess`, `onError`, `validate` and `debounce` of the second call to be dropped, with no message.
MUST expect the second call to reach the cached resource only through `reload()`, and only while the first call's `auto` is truthy.
MUST expect `cached` to be a module-level object that nothing empties, so two components sharing a key share one reactive `data`, `loading` and `error` for the life of the page.
MUST give each distinct request its own `cache` value, or omit `cache` and hold the returned object yourself.
MUST expect `handleError` to end with `throw error` after it has called every `onError`, so `fetch()`, `reload()` and `submit()` reject on every failure.
MUST expect `validate` to route a thrown error and a returned message string through that same `handleError`.
MUST expect `getConfig('fallbackErrorHandler')` to run only when every `onError` in the chain is null.
MUST `await` or `.catch()` a `reload()` fired from a click, because `onError` performs a side effect and does not stop the rejection.
MUST expect a resource carrying a `cache` key to write each success to IndexedDB through `saveLocal` and to read it back once at construction through `getLocal`.
NEVER read a defined `onError` as proof the promise settles.

## values

cache map: `cached`, module-level, never cleared
key: `getCacheKey(options.cache)`
hit returns: the first resource object, options unread
hit side effect: `reload()` when the cached resource's `auto` is truthy
error path: `onError` chain, then `fallbackErrorHandler` only when the chain is empty, then `throw`
offline store: `local.ts` over `idb-keyval`, JSON string per key, no-op when `indexedDB` is undefined
resourceFetcher: `options.resourceFetcher`, then `getConfig('resourceFetcher')`, then `request`

## how

The cache key is an identity, not a hint. Ask what a key names before writing one: it names a request, and two calls that pass the same key are asserting they want the same request and the same reactive object. When they do not, the second call's options are silently thrown away and the bug reads as a stale fetch rather than as a collision.

The error path runs the other way round from most clients: the handler is a place to put a message on screen, not a place to absorb the failure. Write the caller as if every call can reject, and let `onError` do only the visible work.
