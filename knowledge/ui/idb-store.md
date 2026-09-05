---
name: idb-store
description: Without IndexedDB every read and write goes to a plain object that a reload empties, and a real IndexedDB rejection escapes the try block unhandled.
triggers: ["frappe-ui indexeddb store", "cache does not survive reload", "everything i cached disappears when i refresh the page", "the cache is empty again after a reload", "why does my saved data not survive a page refresh", "offline data works in one tab and is gone in a new tab", "the cache tests pass but nothing is actually stored", "how do i check that data is really being written to the browser and not just held in memory", "saving to browser storage fails and nothing is logged anywhere", "i get an unhandled promise rejection with no stack i can trace", "storage quota is full and the app says nothing", "why is caching silently doing nothing on this device", "the cache never works when the page is rendered on the server", "data is not persisting inside the mobile webview"]
product: frappe-ui
---

# idbStore

## paths

src/data-fetching/idbStore.ts — IDBStore, idbStore, set, setMany, get, delete, keys, handleError, validateKey
src/data-fetching/docStore.ts — docStore
src/data-fetching/useList/useList.ts — useList
src/data-fetching/useCall/useCall.ts — useCall

## rules

MUST expect the IndexedDB decision to be made once, in the constructor of the exported instance, from whether `window` exists and carries `indexedDB`.
MUST expect every read and write to route to `memoryStore`, a plain object on the instance, when that decision was false — under server rendering, a test runner, or a webview without IndexedDB.
MUST expect the two paths to present the same interface and to announce nothing, while `memoryStore` lives only as long as the page's JavaScript, so a reload or a new tab starts empty.
MUST test persistence across a reload in a browser, because a run in a memory-store environment exercises the interface and never the storage.
MUST expect `set`, `setMany`, `delete` and the IndexedDB branch of `get` to return the underlying promise rather than await it, so the `try` around them catches only a synchronous throw.
MUST expect an asynchronous rejection — quota exceeded, a blocked connection, a closed database — to escape as an unhandled promise rejection, reaching neither the error handler nor the console.
MUST expect the callers in `useList` and `useCall` to attach `then` with no `catch`, so a real storage failure means the cache silently does not happen.
MUST expect a falsy key to resolve to null before either path runs.

## values

decision: `typeof window !== 'undefined' && !!window.indexedDB`, taken in the constructor
fallback: `memoryStore`, a plain object, one per instance
stored form: a JSON string per key
caught: a synchronous throw only
uncaught: any rejection from the underlying store
handler: `console.error` naming which store, then a resolved null

## how

The fallback is what makes this hard to see. A store that failed loudly would be found on the first run; one that answers correctly and forgets on reload passes every test that stays inside a single page load. Treat "the cache works" as an untested claim until a reload has been part of the test.

The same shape produces the second defect. Returning a promise from inside a `try` reads like error handling and is not, because the block has already exited by the time the promise settles. When a storage write must be observed, await it or attach a `catch` at the call site.
