---
name: list-resource
description: reload asks for page one through the loaded row count in one request, and a row patch reaches every list resource built for that doctype whatever its filters.
triggers: ["createListResource", "listCache", "resourcesByDocType", "reload", "fetch", "update", "setData", "updateRowInListResource", "revertRowInListResource", "deleteRowInListResource", "createResource", "createListResource reload behavior", "list resource row patch", "refreshing the list fires one giant request for everything loaded so far", "the list refresh gets slower every time i load more rows", "why does reloading the list ask the server for hundreds of rows at once", "i see the same rows twice after deleting one", "duplicate rows appear in the list after i add a record", "how do i properly refresh a list after adding or removing a row", "my code runs before the fresh rows arrive", "awaiting the list refresh does not actually wait for the data", "saving one record changed a completely different list on the same page", "a filtered list is showing a row that should not match the filter", "the new field i added is never on the rows even though the server returns it", "a value updated on the server does not appear on the row in the list"]
product: frappe-ui
---

# createListResource

## paths

src/resources/listResource.js — createListResource, listCache, resourcesByDocType, reload, fetch, update, setData, updateRowInListResource, revertRowInListResource, deleteRowInListResource
src/resources/resources.js — createResource

## rules

MUST expect `reload()` to set `start` to 0 and `pageLength` to the loaded row count while `start` is above zero, to restore both in `finally`, and to return the request promise.
MUST expect the `reload()` request to carry the loaded row count as `limit` and `limit_page_length` and 0 as `limit_start`, so a reload after five pages asks the server for all five pages at once.
MUST expect `fetch()` to call `reload()` and to return `undefined`, so awaiting `fetch()` resolves before the request settles.
MUST await `reload()` where later work depends on fresh rows.
MUST expect the list request's success handler to replace `originalData` while `start` is 0 and to concatenate onto it while `start` is above zero, with no deduplication by `name`.
MUST expect the `insert` and `delete` success handlers to call the request-level `list.fetch()`, which asks only for the current `start` and `limit` and therefore repeats those rows past the first page.
MUST call `reload()` after an insert or a delete past the first page.
MUST expect `createListResource` to push every constructed resource into `resourcesByDocType[doctype]`, whatever its filters, fields or cache key.
MUST expect `updateRowInListResource` to walk that whole array and mutate a matching row in place in each resource, comparing `row.name` to `doc.name` loosely and returning early for a doc with no `name`.
MUST include `name` in every doc handed to a write that patches rows.
MUST expect the merge to copy only a key the row already carries, so a field the server returned and the row lacks stays absent.
MUST add that field to the list's `fields` through `update({ fields })` and reload, because a row gains a key only from a response that carried it.
MUST expect each patch to re-run the resource's `transform` over `originalData` and to leave a one-level `row._previousData` copy that only `revertRowInListResource` consumes.

## values

doctype registry: `resourcesByDocType`, module-level, one array per doctype, never pruned
cache: `listCache`, keyed by `getCacheKey(options.cache)`
list url: `getConfig('defaultListUrl')`, else `frappe.client.get_list`
page replaced when: `start` is 0
page appended when: `start` above 0
patch callers: list `setValue` success, list `runDocMethod` success, `fetchOne` success, the document resource's `beforeSubmit` and whitelisted-method success
revert consumer: `revertRowInListResource`

## how

Two different requests hide behind similar names. `resource.reload()` is the page-aware one that rebuilds the whole loaded range and replaces the array; `resource.list.fetch()` is the raw one that asks for the current `start` and `limit` and appends. Every mutation helper reaches for the raw one, which is why a delete past page one leaves duplicates. Read a list resource by asking which of the two a code path called.

The doctype registry is the part that surprises. A write does not patch the list you are looking at; it patches every list resource that was ever constructed for that doctype in this page, including ones whose filters exclude the row. Treat the patch as a rendering convenience and the reload as the truth.
