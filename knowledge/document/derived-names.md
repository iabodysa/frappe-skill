---
name: derived-names
description: A DocType's folder, file and python module are scrub of its name while its controller class is the same name with spaces and hyphens removed and no case change, and a DocType marked custom never reaches that path at all because import_controller returns Document without looking for a file.
triggers: ["scrub", "unscrub", "scrub_dt_dn", "get_module_name", "get_module_app", "get_doctype_module", "load_doctype_module", "get_doc_module", "get_doc_path", "get_module_path", "get_app_path", "get_pymodule_path", "setup_module_map", "get_doctype_app", "get_doctype_app_map", "import_controller", "get_controller", "DocType {} not found", "Module {} not found", "Module import failed for", "is not a subclass of BaseDocument", "controller not loading", "doctype folder name", "class name of a doctype", "where does frappe look for a controller", "my code file for this record type is never used and nothing complains", "the custom logic i wrote never runs and there is no error anywhere", "why is my code being ignored for this record type", "it says the module cannot be found when i open this record type", "renaming the folder broke the whole thing", "it complains the class is missing even though the file is right there", "two apps use the same module name and the files load from the wrong one", "the folder name and the class name do not match and i do not know which is right", "what do i name the folder and the file for a new record type", "the name with the capital letters in it will not load at all", "my override class is rejected and i cannot tell why"]
product: frappe
---

# Derived Names

## paths

frappe/__init__.py — scrub, unscrub, get_module_path, get_app_path, get_pymodule_path, setup_module_map, get_doctype_app, get_module_list
frappe/modules/utils.py — scrub_dt_dn, get_doc_path, get_doctype_module, load_doctype_module, get_module_name, get_module_app, get_doc_module, get_doctype_app_map
frappe/model/base_document.py — import_controller, get_controller, DOCTYPES_FOR_DOCTYPE

## rules

MUST name a DocType's folder and its python file `scrub(doctype)`, because `get_module_name` builds `<app>.<module>.doctype.<scrubbed doctype>.<scrubbed doctype>` and every loader goes through it.
MUST name the controller class the DocType name with spaces and hyphens removed and NOTHING lowercased, because `import_controller` computes the class name with two `replace` calls and never calls `scrub`.
NEVER treat `unscrub` as the inverse of `scrub`; it splits on underscore and hyphen and applies `title()`, so any name carrying an acronym or an internal capital does not survive the round trip.
MUST expect a DocType whose `custom` field is set to get `Document`, or `NestedSet` when it is a tree, with no module and no file consulted, so a controller file written for a custom DocType is never imported and nothing reports it.
MUST list a module in the app's `modules.txt` before any path derives from it; `setup_module_map` builds the module-to-app map from that file alone, and `get_module_app` throws `Module {} not found` as a DoesNotExistError for a module missing from it.
NEVER let two apps declare one module name in `modules.txt`; `setup_module_map` emits a warning and keeps the app it saw last, so every path for that module silently resolves into the wrong app.
MUST expect `get_doctype_module` to read a cached DocType-to-module map and to throw `DocType {} not found` as a DoesNotExistError when the DocType is not in it.
MUST expect a missing controller module to raise ImportError from `load_doctype_module` carrying `Module import failed for`, and a module that imports while missing the class to raise ImportError from `import_controller`.
MUST make an overriding class a subclass of `BaseDocument`, because `import_controller` raises ImportError naming `is not a subclass of BaseDocument` and no earlier check catches it.
NEVER pass a mixed-case path element to `get_app_path`, `get_module_path` or `get_pymodule_path`; every join part is scrubbed unless one of the parts is exactly `public`, so the derived path is lowercased and the miss shows up only as a missing file.
MUST expect `get_doc_path` to raise a ValueError when the scrubbed doctype and name resolve outside the module directory.
MUST reach a doc's own module through `get_doc_module`, which derives `<app>.<module>.<scrubbed doctype>.<scrubbed name>.<scrubbed name>` — the record's NAME, not its DocType, is the last two segments.

## values

scrub: space and hyphen to underscore, then lowercase
unscrub: underscore and hyphen to space, then title case
controller module: <app>.<module>.doctype.<scrub(doctype)>.<prefix><scrub(doctype)><suffix>
controller class: doctype with " " and "-" removed, case untouched
doc folder: <module path>/<scrub(doctype)>/<scrub(name)>
module path: <app package dir>/<scrub(module)>
raises DoesNotExistError: get_doctype_module on an unknown DocType, get_module_app on a module missing from modules.txt
raises ImportError: load_doctype_module on a missing module, import_controller on a missing or non-BaseDocument class
raises nothing: custom=1 short-circuit, a scrubbed join part, a module name claimed by two apps

## how

Three different spellings of one DocType name are in play at once, and only two of them are `scrub`.
The folder and the file are scrubbed; the class is the name with its separators deleted and its capitals
kept. A DocType named with an acronym is the case that exposes this: the file is all lowercase and the
class is not, and getting either wrong produces an ImportError that names the other one.

The quiet failures all sit before the import. A custom DocType returns the base class without ever
deriving a path, a module missing from modules.txt cannot be mapped to an app, and a module declared by
two apps resolves to whichever app was read last. None of those three prints anything the reader will
be looking at, and all three end in behaviour that simply does not run.

Derive names, do not compose them by hand. `get_module_name`, `get_doc_path` and `get_doc_module` each
apply `scrub` at every segment, so a caller that formats its own string is one capital letter away from
a path that exists nowhere.
