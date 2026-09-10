---
name: test-factory
description: erpnext ships its own idempotent get-or-create test factories for common masters, usable directly by any app's tests.
triggers: ["make_item", "create_supplier", "test factory for Item", "test factory for Supplier", "get or create test fixture", "idempotent test helper", "reuse erpnext test factory", "writing my own Item factory for tests"]
product: erpnext
---

# Test factory

## paths

erpnext/stock/doctype/item/test_item.py — make_item
erpnext/buying/doctype/supplier/test_supplier.py — create_supplier

## rules

MUST call `erpnext.stock.doctype.item.test_item.make_item` to get or create a test Item instead of writing a new factory; it is idempotent.
MUST call `erpnext.buying.doctype.supplier.test_supplier.create_supplier` to get or create a test Supplier the same way.
MUST use either from any app's test module that needs a standard fixture of that master; both are importable, not restricted to erpnext's own suite.

## how

Both functions already handle the get-or-create check for their doctype, so a new test that re-implements "look it up, else insert it" for Item or Supplier duplicates a helper the framework's own app already ships.
