---
name: form-write
description: accept writes one value per declared Web Form field and defaults a missing key to an empty string, so an edit that omits a declared field blanks it.
triggers: ["accept", "WebForm.web_form_fields", "remove_file_by_url", "Web Form", "File", "You need to be in developer mode to edit a Standard Web Form", "Following fields are missing:", "Mandatory Information missing:", "web form field not saved", "web form accept missing field", "editing one field wiped out all the other fields in the record", "why did my saved data get blanked after the user updated the entry", "the uploaded file vanished from the server after an edit", "the attachment got deleted and there is no way to get it back", "hidden fields on my form are being cleared on every update", "how do i keep a value from being erased when the user edits", "extra keys i send in the payload are just ignored and never saved", "a field i added to the record is never written from the website", "the record loses data whenever we submit a partial update", "why is the entry saved twice when there is an upload"]
product: frappe
---

# Web Form write

## paths

frappe/website/doctype/web_form/web_form.py — accept, WebForm.web_form_fields
frappe/core/doctype/file/utils.py — remove_file_by_url

## rules

MUST post every declared field on an edit, including the ones the user did not edit; the write loop iterates the form's declared fields and sets each one from the payload with an empty string as the default.
NEVER hide a field on a Web Form and expect its stored value to survive an edit. A hidden declared field is still in the loop and is still blanked when the client omits it.
MUST read an omitted Attach or Attach Image field as worse than blanked: the branch that records the current file for removal has no continue, so the field is emptied and the file it pointed at is deleted after the save.
NEVER expect a key the payload carries but the form does not declare to be written. The loop asks the payload only for names in the form's own field table, which is the protection a hand-written endpoint calling doc.update on request data gives up.
MUST add a field to the Web Form for it to be written; a field absent from the form is ignored and never defaulted from the request.
MUST expect a base64 value in an Attach field to be split off, saved as a File and written back over the field in a second save that runs with ignore_permissions.

## values

loop source: the Web Form's web_form_fields table
missing key default: the empty string
attach with base64 data: queued as a File, and cleared on the document first when the document is new
attach empty with a stored value: queued for removal by URL and blanked in the same pass
after the file pass: a second doc.save with ignore_permissions writes the file URLs

## how

The write is field-driven, not payload-driven. The form's own field table decides both what may be written and what is written, which is why the portal is safe against an injected key and unsafe against a partial
payload — the same loop produces both. A client that sends a diff destroys the fields it left out.

So an edit page has one correct shape: render every declared field and post every declared field,
whether or not it is visible. Anything you want kept out of the user's hands is kept off the form
entirely and defaulted in the DocType, never hidden on the form.

Attachments are the case worth checking by hand, because their failure removes a file from disk
rather than clearing a column, and there is no way back from it.
