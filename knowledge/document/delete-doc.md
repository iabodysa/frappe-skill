---
name: delete-doc
description: force does not narrow the link check delete_doc runs before removing a row, it skips the call to check_if_doc_is_linked and check_if_doc_is_dynamically_linked entirely, so a forced delete can leave live references pointing at a name that no longer exists.
triggers: ["delete_doc", "check_if_doc_is_linked", "check_if_doc_is_dynamically_linked", "Standard DocType can not be deleted.", "This document can not be deleted right now as it", "delete a linked document", "force delete bypasses link check", "i removed a record and now other records point at something that no longer exists", "forcing the delete did not warn me that something was still using it", "why did it let me delete a record that other records still reference", "links are broken all over the place after i removed one record", "the delete refused at first and after i forced it everything broke", "nothing told me the record was still in use and now half the list is broken", "opening a record shows a link to a name that is not there anymore", "how do i check what is still using a record before i remove it", "the reference field is still holding the name of something i deleted", "clicking the link on the form goes to a record that does not open"]
product: frappe
---

# delete_doc and force

## paths

frappe/model/delete_doc.py — delete_doc, check_if_doc_is_linked, check_if_doc_is_dynamically_linked

## rules

MUST expect `force=1` to skip `check_if_doc_is_linked` and `check_if_doc_is_dynamically_linked` outright, because both calls sit inside one `if not force:` block.
NEVER read `force` as asking the link check to run and then waiving what it finds; the check itself never executes.
MUST expect a forced delete to leave any live Link or Dynamic Link field pointing at the deleted name, since nothing after the skipped block re-checks or clears them.

## how

`force` never inspects what the link checks would find, because both calls sit inside an `if not force:` block that is not entered at all. Deleting with `force=1` while another document still links to the row neither reports that link nor clears it: the row goes and every Link and Dynamic Link field pointing at it keeps the name that no longer resolves.
