---
name: document-resource
description: doctype and name are read once at construction, so a resource never follows a route parameter, and every write copies the whole document into one previousDoc property that the next write overwrites.
triggers: ["createDocumentResource", "documentCache", "setValueOptions", "save", "reload", "setDoc", "transform", "getCachedDocumentResource", "updateRowInListResource", "revertRowInListResource", "createDocumentResource does not follow route change", "document resource previousDoc overwritten", "the detail page still shows the previous record after i click a different one", "changing the id in the address bar does not load the new record", "why does the same record keep showing when i navigate between them", "saving sent fields i never put in the form", "the save request includes extra junk fields", "one of my two edits was rolled back to an older value", "saving two fields quickly loses one of them", "how do i make the page follow the record in the route", "an error while saving put the wrong old values back", "the row in the list does not update after i save the record"]
product: frappe-ui
---

# createDocumentResource

## paths

src/resources/documentResource.js — createDocumentResource, documentCache, setValueOptions, save, reload, setDoc, transform, getCachedDocumentResource
src/resources/listResource.js — updateRowInListResource, revertRowInListResource
src/data-fetching/useDoc/useDoc.ts — useDoc

## rules

MUST expect the resource to key `documentCache` on the `doctype` and `name` handed to the constructor, and to return the cached object on a second call with the same pair.
MUST expect a falsy `doctype` or `name` to return `undefined` before anything is built.
MUST construct a new resource to follow a record change, by keying the routed component on the record identity, or MUST reach for `useDoc`, which takes `name` as a ref or getter and rebuilds its url as a computed.
MUST expect `save` to serialize `out.doc` and to delete only `doctype` and `name`, so every other own property travels as a fieldname.
MUST keep a derived value out of what `transform` returns, and MUST compute it in a `computed` beside the resource.
MUST expect `transform` to replace the whole document, and to run on the get success, the `setValue` success, `setDoc`, a whitelisted method response carrying a matching doc, and the offline load.
MUST expect `beforeSubmit` to write `out.previousDoc` as one JSON string of the whole document and to assign the submitted fields onto `out.doc` before the request returns.
MUST expect `onError` to restore that whole string over `out.doc`, and MUST expect a second write started while the first is in flight to overwrite `out.previousDoc` with a copy that already carries the first write's optimistic change.
MUST serialize two writes that can overlap on one document resource, and MUST call `reload()` after a write error to re-read the record.
MUST expect the same handlers to patch and revert the row in every constructed list resource for that doctype.

## values

cache: `documentCache`, reactive, keyed on doctype and name
update url: `getConfig('defaultDocUpdateUrl')`, else `frappe.client.set_value`
get url: `getConfig('defaultDocGetUrl')`, else `frappe.client.get`
delete url: `getConfig('defaultDocDeleteUrl')`, else `frappe.client.delete`
method url: `getConfig('defaultRunDocMethodUrl')`, else `run_doc_method`
previousDoc: `out.previousDoc`, one per resource, the whole document as a JSON string
debounced write: `setValueDebounced`, `options.debounce` else 500
auto: true unless `options.auto` is passed
offline: `saveLocal` on get success, `getLocal` once at construction, `deleteLocal` on get error

## how

The identity is frozen at construction and the cache hands the same object back, so a detail screen that changes record without changing component keeps rendering the first record. The fix is not a watcher on the route; it is a `key` on the component, or the composable that was built to take a changing name.

Every write is optimistic and the rollback is one whole-document string in `out.previousDoc`. That works for one write at a time and quietly loses data for two, so decide up front whether a screen can have two writes in flight — a field-level save on blur across a form usually can — and serialize them if it can.
