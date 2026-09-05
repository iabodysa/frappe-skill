---
name: tree
description: An app is a python package one level below its repository, and every DocType is a directory of six files named after itself.
triggers: ["app_name", "doc_events", "scheduler_events", "Item", "TestItem", "get_doc_path", "scrub", "Valuation Rate is mandatory if Opening Stock entered", "Fixed Asset Item must be a non-stock item.", "Asset Category is mandatory for Fixed Asset item", "app structure", "directory layout", "the framework says my record type does not exist even though the files are there", "why is my new record type not found after i created the folder", "i renamed the folder and now nothing loads", "the python file is not being imported and the type shows as missing", "my hooks file is being ignored completely", "the event handlers i registered never fire", "where exactly is the code file for a given record type supposed to live", "how do i name the folder for a record type with spaces in the name", "i added a new group of record types and none of them appear", "the test file is not picked up by the test runner", "should the readme sit next to the code folder or inside it"]
product: erpnext
---

# Tree

## paths

erpnext/hooks.py — app_name, doc_events, scheduler_events
erpnext/modules.txt
erpnext/patches.txt
erpnext/stock/doctype/item/item.json
erpnext/stock/doctype/item/item.py — Item
erpnext/stock/doctype/item/item.js
erpnext/stock/doctype/item/item_list.js
erpnext/stock/doctype/item/test_item.py — TestItem
frappe/modules/utils.py — get_doc_path, scrub

## rules

MUST put a DocType under `<app>/<module>/doctype/<scrubbed name>/`, where the scrubbed name is the
DocType name lowercased with spaces turned to underscores.
MUST name every file in that directory after the directory itself; the loader finds the controller,
the schema, the form script and the test by that name alone.
MUST declare the module in `modules.txt` before any DocType inside it can be found.
MUST write a repository-level file — the readme, the license, the package manifest — one level ABOVE
the python package, never inside it.
NEVER create a module directory without an `__init__.py`; python will not import it and the loader
reports the DocType as missing rather than as broken.
NEVER put a second DocType's file in a DocType directory; the directory name is the identifier.

## values

repository root: readme, license, pyproject, package.json, the python package
python package: hooks.py, modules.txt, patches.txt, one directory per module
module: doctype, report, page, print_format, workspace, dashboard_chart, number_card
doctype directory: json, py, js, list js, test py, optional templates
test file: test_ prefix on the scrubbed name
child table: the same shape, with istable set in the json

## how

The tree is not a convention a reader may vary. The loader derives every path from the DocType name,
so a directory renamed by hand and a file that does not match its directory both read as an absent
DocType rather than as an error.

Two levels are easy to confuse and cost a day when confused. The repository is the outer level and
carries what a package manager and a human read. The python package is the inner level, one name
deeper and usually the same word, and carries what the framework reads. A hook file placed in the
outer level is never loaded and never complained about.

When adding anything, find the module first and let the module decide the path. A reader who starts
from the file kind rather than from the module invents a directory the loader will not look in.
