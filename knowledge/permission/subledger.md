---
name: subledger
description: ERPNext writes GL Entry and Stock Ledger Entry itself, and its own writer sets flags.ignore_permissions before submit, so no role or DocPerm row governs a posted ledger row.
triggers: ["make_entry", "Please set", "Please mention", "gl entry stock ledger entry permission bypass", "erpnext ignores permissions on submit", "i removed every role from the ledger table and entries still get created", "permissions on the accounting entries table do nothing at all", "why can a user create ledger rows when he has no rights on that table?", "the stock movement rows ignore my permission rules", "blocking the ledger did not stop postings", "who is actually allowed to post to the accounts ledger?", "auditing rights on the ledger gives me the wrong answer", "i want to stop a user from posting stock movements but restrictions have no effect", "posting happens even though the role has no create right on the entries table", "where should i put the restriction if the ledger ignores it?"]
product: erpnext
---

# Subledger

## paths

erpnext/accounts/general_ledger.py — make_entry
erpnext/stock/stock_ledger.py — make_entry

## rules

MUST expect a posted GL Entry or Stock Ledger Entry to bypass DocPerm and role checks entirely, because make_entry in each module sets flags.ignore_permissions before calling submit.
NEVER audit who may create a ledger row by reading GL Entry or Stock Ledger Entry DocPerm rows; the row's own writer already exempted itself, and the DocPerm rows govern only a caller that builds and submits the doc directly.
MUST place the write control on the transaction that calls make_entry — the Sales Invoice, the Stock Entry, the Journal Entry — since that is the only layer still checked.

## values

GL Entry submit: flags.ignore_permissions = 1, set inside make_entry
Stock Ledger Entry submit: flags.ignore_permissions = 1, set inside make_entry

## how

Both ledgers exist to record what a transaction already decided, not to be decided over again, so their own writer removes itself from the permission system rather than asking the poster's role to also cover the ledger DocType. Reading the GL Entry or Stock Ledger Entry DocPerm rows therefore answers a question nobody is asking; the write that matters already happened one level up, on the transaction the user actually submitted.
