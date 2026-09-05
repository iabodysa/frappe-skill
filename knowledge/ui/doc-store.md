---
name: doc-store
description: One ref per doctype and name is shared by every useDoc in the page, and getDoc deletes that ref before returning it once the entry is five minutes old.
triggers: ["frappe-ui doc store shared ref", "getDoc cache eviction", "the form i was editing suddenly reset to the saved values", "two screens on the same record keep overwriting each other", "opening the record again after a while throws an error", "it says cannot read property of undefined when i revisit a page", "the page crashes only after i leave it open for a long time", "why did my unsaved edits disappear when something refreshed", "how do i stop one component's refresh from changing another", "record data is shared between components and i want it separate", "it works while developing but breaks after a long session", "coming back to the same record a few minutes later breaks the page"]
product: frappe-ui
---

# docStore

## paths

src/data-fetching/docStore.ts — DocStore, docStore, getDoc, setDoc, loadDoc, cleanup, isStale, clearAll, setCacheTimeout
src/data-fetching/useDoc/useDoc.ts — useDoc
src/data-fetching/idbStore.ts — idbStore

## rules

MUST expect `docStore` to be one exported instance shared by every component in the page.
MUST expect `getDoc` to create a `ref(null)` for a key only on first sight and to return that same ref on every later call, so two `useDoc` calls on one record read one ref.
MUST expect `setDoc` to assign the whole document onto that ref rather than merge into it, so a save or a background refetch started anywhere replaces what every other mounted `useDoc` on that record renders.
MUST expect a fetch success and a `setValue` success in `useDoc` both to call `setDoc`.
MUST expect `getDoc` to fire `loadDoc` without awaiting it when the entry is stale, and MUST expect `cleanup` to delete the key from the map before its first await, so the return line finds nothing and hands back `undefined`.
MUST expect `useDoc` to read `.value` on that result with no null check, so revisiting the same record more than the cache timeout after its last fetch throws inside the component's setup.
MUST hold the record in a component that stays mounted, or refetch on entry, where a route returns to a record after a long gap.
MUST expect the staleness clock to be the last fetch time per key, and MUST pass at least one minute to `setCacheTimeout`.

## values

map: `docs`, key `<doctype>/<name>`, value `Ref<Doc | null>`
clock: `lastFetched`, one timestamp per key
cacheTimeout: 5 minutes, `setCacheTimeout` in minutes, under 1 throws
persistence: `idbStore` under the store prefix
getDoc branches: create and first load, stale reload, plain return
cleanup: deletes the map entry and the timestamp, then the IndexedDB row

## how

The store trades isolation for consistency and does not say so. Two screens on one record stay in step for free, and neither can opt out — a background refetch on one replaces the other's document mid-edit. Ask, before binding a form to `useDoc`, whether anything else in the page holds the same record.

The staleness path is where the sharing turns into a crash rather than a surprise: the reload deletes the entry synchronously and the getter returns undefined for the key it just removed. It only fires on a revisit past the timeout, which is why it survives development and appears in a long session.
