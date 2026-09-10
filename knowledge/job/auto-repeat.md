---
name: auto-repeat
description: Auto Repeat clones exactly one reference document into one new document of the same doctype on a fixed cadence; it is not a fan-out generator.
triggers: ["Auto Repeat", "create_documents", "make_new_document auto repeat", "clone a document on a schedule", "recurring document generator", "generate N documents per day from two tables", "auto repeat only makes one document", "fan out documents from a join"]
product: frappe
---

# Auto Repeat

## paths

frappe/automation/doctype/auto_repeat/auto_repeat.py — AutoRepeat.create_documents, AutoRepeat.make_new_document

## rules

MUST expect `create_documents` -> `make_new_document` -> `frappe.copy_doc(reference_doc, ignore_no_copy=False)` to produce exactly one new document of the same doctype as the one reference document configured on the Auto Repeat record.
NEVER configure one Auto Repeat record expecting it to fan out N new documents per run from a join of two other tables; it clones one document, once per cadence.
MUST create one Auto Repeat record per resulting document when several independent repeats are needed.

## how

The mechanism is a scheduled `copy_doc` call bound to one reference document; the cadence decides WHEN it runs, never HOW MANY documents one run produces.
