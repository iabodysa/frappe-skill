# The files an app is made of — which one declares behaviour

A file changes the running site only if something READS it, so the test on any file in an app is one
question: name the line that reads this file. A file with no reader declares nothing however
official it looks. The second test is the name: the framework resolves a module, a class, a folder
and an asset by DERIVING each from another name, and a derived path that misses raises nothing for
most of them.

| File | Verdict | Read by |
|---|---|---|
| `hooks.py` | declares — the only wiring an app has | one reader per key, resolved through the app registry |
| `patches.txt` | declares — an ordered run list | the patch handler, in file order |
| `modules.txt` | declares — the module allow-list | the module path resolver |
| `<dt>/<dt>.json` | declares — schema, permissions, naming | the schema sync on migrate |
| `<dt>/<dt>.py` | declares — the class imported under a DERIVED name | the controller loader |
| `<dt>/<dt>.js` | declares — client behaviour, found by filename | the form meta builder |
| `<dt>/test_<dt>.py` | describes — changes nothing on a live site | the test runner only |
| `<dt>/test_records.json` | declares — for the test database only | the test record builder, once per site |
| `fixtures` in `hooks.py` | declares — a DocType name and a folder of rows | the fixture import on every migrate |
| the Workspace record | declares — the navigation | the desk, from the record and not the folder |
| `<app>/config/` | describes — scaffolded and unread | nothing |

A derived path that resolves to no file fails loudly for a controller, a patch and a report module,
and silently for a form asset, a dashboard module, a notification body and a workspace content
block — so a name must be derived and compared against the tracked files, never checked by eye.

## Settled by

| what it settles | leaf |
|---|---|
| the transaction around a patch and the stamp on any normal return | `knowledge/bench/patches.md` |
| the nineteen importable folders and the permanent skip | `knowledge/bench/standard-json.md` |
| the forced re-import and the per-file commit | `knowledge/bench/fixtures.md` |
| the phase each file is read in | `knowledge/bench/migrate.md` |
| the naming the DocType JSON declares | `knowledge/document/autoname.md` |
| which of the JSON's field properties the server enforces | `knowledge/document/validation.md` |
| why the record and not the folder is the navigation | `knowledge/desk/workspace.md` |
| the once-per-site build of `test_records.json` | `knowledge/bench/records.md` |
| the package one level below the repository, and the six files of a DocType | `knowledge/bench/tree.md` |
| the merged dict that stores a key no reader function asks for | `knowledge/bench/hooks.md` |
| the folder, module and class a name derives, and the custom DocType with none | `knowledge/document/derived-names.md` |
