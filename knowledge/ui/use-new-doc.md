---
name: use-new-doc
description: doc holds only what was typed — submit returns the created document and writes nothing back, so a second submit creates a second record.
triggers: ["useNewDoc submit creates duplicate", "new doc form state", "clicking save twice creates two identical records", "why did submitting the form a second time make a duplicate", "the form still shows what i typed after it saved instead of the real record", "the id of the new record is empty right after creating it", "fields the server fills in are blank on my screen after saving", "the default values set by the backend never show up in the form", "how do i clear the form after it saves", "the generated number is missing until i reload the page", "user double clicks the create button and we get two entries", "why is the saved record different from what my form shows", "how do i get the record that was actually created back from the save"]
product: frappe-ui
---

# useNewDoc

## paths

src/data-fetching/useNewDoc/useNewDoc.ts — useNewDoc, submit
src/data-fetching/docStore.ts — docStore
src/data-fetching/useCall/useCall.ts — useCall

## rules

MUST expect `doc` to be the reactive object built from the initial values once, and MUST expect the params function to re-read its fields on every submit.
MUST expect `submit` to resolve to the document read back from `docStore` after the response is stored, and to assign nothing onto `doc`.
MUST treat the resolved document as the record after creation, because an autoname, a field default and a controller-set value appear only there while a form bound to `doc` still shows what was typed.
MUST expect `doc` to keep its fields after a successful submit, so a second call posts the same values as a new create and produces a second record.
MUST discard the instance, or block re-entry, once submit resolves.
MUST expect the create to be a POST to the document endpoint for the doctype.

## values

doc: `reactive(initialValues)`, never written back, never cleared
params: read from `doc` on each submit, each value unwrapped
submit resolves to: the stored document from `docStore`
method: POST
immediate: false

## how

The composable owns the draft and the store owns the record, and the two never meet. That is workable as long as the code treats the resolved value as the record and the reactive object as the values that were typed, which are now spent. The failure is a form that stays on screen after creating: it is still bound to `doc`, still editable, and its button still creates.

Route away, or replace the instance, on the resolution — not on the click.
